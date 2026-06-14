import http.server
import json
import math
import os
import urllib.parse
import sqlite3
import csv
from io import StringIO
from datetime import datetime, time, timedelta

# --- CONSTANTS & CONFIGURATION ---
PORT = 8000
DB_FILE = "attendance.db"

# Default case study data for initialization
DEFAULT_STUDENTS = [
    ("S101", "Alice Smith", "alice@school.edu", "parent.alice@home.com", 8, 1, 1, "av-indigo", "AS"),
    ("S102", "Bob Jones", "bob@school.edu", "parent.bob@home.com", 5, 1, 4, "av-orange", "BJ"),
    ("S103", "Charlie Brown", "charlie@school.edu", "parent.charlie@home.com", 0, 0, 10, "av-teal", "CB")
]

DEFAULT_DEVICES = [
    ("DEV_ROOM_101", 1, "Biometric Face Scanner (Room 101)"),
    ("DEV_MAIN_GATE", 1, "RFID Badge Reader (Main Entrance)"),
    ("DEV_INACTIVE", 0, "Deactivated Scanner (DEV_INACTIVE)")
]

SCHEDULES = {
    "SCH_CS101": { "id": "SCH_CS101", "courseId": "CS101", "title": "CS101 (Intro to CS)", "startTime": "09:00", "endTime": "10:30", "lat": 37.7749, "lon": -122.4194, "radius": 50 },
    "SCH_MATH201": { "id": "SCH_MATH201", "courseId": "MATH201", "title": "MATH201 (Calculus II)", "startTime": "11:00", "endTime": "12:30", "lat": 37.7749, "lon": -122.4194, "radius": 50 }
}

# In-memory deduplication cache: maps studentId_scheduleId -> lastScanTime_string (Simulating Redis)
duplicate_cache = {}
auth_tokens = set(["authenticated_admin"]) # Simulating active session tokens

# --- SQLITE DATABASE HANDLERS ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id TEXT PRIMARY KEY, name TEXT, email TEXT, parentEmail TEXT, 
                        presents INTEGER, lates INTEGER, absents INTEGER, avatarClass TEXT, initials TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
                        id TEXT PRIMARY KEY, active INTEGER, name TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, time TEXT, message TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, sender TEXT, text TEXT)''')

    # Seed initial data if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", DEFAULT_STUDENTS)
        cursor.executemany("INSERT INTO devices VALUES (?, ?, ?)", DEFAULT_DEVICES)
        cursor.execute("INSERT INTO logs (category, time, message) VALUES (?, ?, ?)", 
                       ("system", datetime.now().strftime("%I:%M %p"), "AttendSmart SQL verification services initiated."))
        conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- MATHEMATICAL UTILITIES ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000.0  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

# --- HTTP REQUEST HANDLER CLASS ---
class AttendSmartHTTPHandler(http.server.BaseHTTPRequestHandler):

    def send_json_response(self, data, status_code=200):
        try:
            response_bytes = json.dumps(data).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_bytes)
        except Exception as e:
            print(f"[Server ERROR] wfile writing failed: {e}")

    def is_authenticated(self):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return False
        token = auth_header.split(" ")[1]
        return token in auth_tokens

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        if path.startswith("/api/"):
            # Authentication protection for API GET endpoints
            if path != "/api/reports/download" and not self.is_authenticated():
                self.send_json_response({"error": "Unauthorized Access"}, 401)
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            
            if path == "/api/students":
                cursor.execute("SELECT * FROM students")
                students = {row['id']: dict(row) for row in cursor.fetchall()}
                self.send_json_response(students)
            elif path == "/api/devices":
                cursor.execute("SELECT * FROM devices")
                devices = {row['id']: dict(row) for row in cursor.fetchall()}
                # Convert active integer to boolean
                for d in devices.values(): d['active'] = bool(d['active'])
                self.send_json_response(devices)
            elif path == "/api/logs":
                cursor.execute("SELECT category, time, message FROM logs ORDER BY id DESC LIMIT 50")
                self.send_json_response([dict(r) for r in cursor.fetchall()])
            elif path == "/api/alerts":
                cursor.execute("SELECT time, sender, text FROM alerts ORDER BY id DESC LIMIT 20")
                self.send_json_response([dict(r) for r in cursor.fetchall()])
            elif path.startswith("/api/reports/download"):
                # Check Auth token from query param (easier for window.open)
                qs = urllib.parse.parse_qs(url_parsed.query)
                token = qs.get("token", [""])[0]
                if token not in auth_tokens:
                    self.send_json_response({"error": "Unauthorized Access"}, 401)
                    conn.close()
                    return

                # Generate CSV Report
                cursor.execute("SELECT id, name, email, presents, lates, absents FROM students")
                students = cursor.fetchall()
                
                si = StringIO()
                cw = csv.writer(si)
                cw.writerow(["Student ID", "Name", "Email", "Presents", "Lates", "Absents", "Attendance %"])
                
                for s in students:
                    total = s['presents'] + s['lates'] + s['absents']
                    att_rate = ((s['presents'] + s['lates']) / total * 100) if total > 0 else 0
                    cw.writerow([s['id'], s['name'], s['email'], s['presents'], s['lates'], s['absents'], f"{att_rate:.1f}%"])
                
                csv_data = si.getvalue().encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", 'attachment; filename="attendance_report.csv"')
                self.send_header("Content-Length", str(len(csv_data)))
                self.end_headers()
                self.wfile.write(csv_data)
            else:
                self.send_json_response({"error": "Endpoint not found"}, 404)
            
            conn.close()
            return

        # --- STATIC FILE SERVING PATHS ---
        if path == "/" or path == "":
            file_to_serve = "home.html"
        else:
            file_to_serve = path.lstrip("/")

        base_dir = os.path.abspath(os.path.dirname(__file__))
        target_path = os.path.abspath(os.path.join(base_dir, file_to_serve))
        if not target_path.startswith(base_dir):
            self.send_error(403, "Access Denied")
            return

        if os.path.exists(target_path) and os.path.isfile(target_path):
            content_type = "text/html"
            if file_to_serve.endswith(".css"): content_type = "text/css"
            elif file_to_serve.endswith(".js"): content_type = "application/javascript"
            
            with open(target_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        try: payload = json.loads(body) if body else {}
        except Exception:
            self.send_json_response({"error": "Malformed JSON"}, 400)
            return

        if path == "/api/login":
            email = payload.get("email", "").strip()
            password = payload.get("password", "")
            if email == "admin@attendsmart.com" and password == "admin123":
                self.send_json_response({"token": "authenticated_admin"})
            else:
                self.send_json_response({"error": "Invalid administrative credentials"}, 401)
            return

        # Authentication protection for other POST endpoints
        if not self.is_authenticated():
            self.send_json_response({"error": "Unauthorized Access"}, 401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        def log_event(msg, cat):
            cursor.execute("INSERT INTO logs (category, time, message) VALUES (?, ?, ?)", 
                           (cat, datetime.now().strftime("%I:%M %p"), msg))
            conn.commit()

        if path == "/api/students/onboard":
            sid, name = payload.get("studentId", "").strip(), payload.get("name", "").strip()
            email, parent_email = payload.get("email", "").strip(), payload.get("parentEmail", "").strip()

            cursor.execute("SELECT id FROM students WHERE id = ?", (sid,))
            if cursor.fetchone():
                self.send_json_response({"error": f"Student ID {sid} already exists"}, 400)
                conn.close()
                return

            import random
            avatar_class = random.choice(["av-indigo", "av-orange", "av-teal", "av-rose", "av-blue"])
            initials = "".join([n[0] for n in name.split()]).upper()[:2]

            cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (sid, name, email, parent_email, 0, 0, 10, avatar_class, initials))
            log_event(f"Database: Onboarded new student profile S{sid} ({name}).", "system")
            conn.close()
            self.send_json_response({"status": "success", "id": sid})
            return

        elif path == "/api/devices/toggle":
            did = payload.get("deviceId", "")
            cursor.execute("SELECT active FROM devices WHERE id = ?", (did,))
            row = cursor.fetchone()
            if not row:
                self.send_json_response({"error": "Device not found"}, 404)
                conn.close()
                return
            
            new_status = 0 if row['active'] else 1
            cursor.execute("UPDATE devices SET active = ? WHERE id = ?", (new_status, did))
            status_str = "ONLINE" if new_status else "OFFLINE"
            log_event(f"Device Configuration updated: Reader {did} toggled to {status_str}.", "system")
            conn.close()
            self.send_json_response({"status": "success", "active": bool(new_status)})
            return

        elif path == "/api/reset":
            cursor.execute("DELETE FROM students")
            cursor.execute("DELETE FROM devices")
            cursor.execute("DELETE FROM logs")
            cursor.execute("DELETE FROM alerts")
            conn.commit()
            conn.close()
            
            # Reinitialize defaults
            init_db()
            duplicate_cache.clear()
            self.send_json_response({"status": "success"})
            return

        elif path == "/api/checkin":
            sid = payload.get("studentId", "")
            sched_id = payload.get("scheduleId", "")
            did = payload.get("deviceId", "")
            lat, lon = float(payload.get("lat", 0)), float(payload.get("lon", 0))
            biometric_score = float(payload.get("biometricScore", 0))
            time_string = payload.get("timeString", "08:55")
            
            cursor.execute("SELECT * FROM students WHERE id = ?", (sid,))
            student = cursor.fetchone()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (did,))
            device = cursor.fetchone()
            schedule = SCHEDULES.get(sched_id)

            h_parsed, m_parsed = map(int, time_string.split(":"))
            ampm = "AM" if h_parsed < 12 else "PM"
            display_h = h_parsed if h_parsed <= 12 else h_parsed - 12
            display_h = 12 if display_h == 0 else display_h
            display_time_str = f"{str(display_h).zfill(2)}:{str(m_parsed).zfill(2)} {ampm}"

            def local_log(msg, cat):
                cursor.execute("INSERT INTO logs (category, time, message) VALUES (?, ?, ?)", 
                               (cat, display_time_str, msg))

            local_log(f"Check-in request received from reader <code>{did}</code> for student {student['name'] if student else sid}.", "ingest")

            if not student:
                local_log(f"Check-in REJECTED: Student ID '{sid}' not found in directory.", "error")
                conn.commit()
                conn.close()
                self.send_json_response({"success": False, "reason": "INVALID_STUDENT_ID"})
                return

            if not device:
                local_log(f"Check-in REJECTED: Hardware scanner ID '{did}' is not registered on network.", "error")
                conn.commit()
                conn.close()
                self.send_json_response({"success": False, "reason": "UNAUTHORIZED_DEVICE"})
                return
            
            if not device['active']:
                local_log(f"Check-in REJECTED: Reader ID '{did}' is deactivated/offline.", "error")
                conn.commit()
                conn.close()
                self.send_json_response({"success": False, "reason": "DEVICE_DEACTIVATED"})
                return

            dup_key = f"{sid}_{sched_id}"
            if dup_key in duplicate_cache:
                local_log("Check-in SKIPPED: Duplicate card/face swipe registered within 60s window.", "error")
                conn.commit()
                conn.close()
                self.send_json_response({"success": False, "reason": "DUPLICATE_SCAN_DETECTED"})
                return
            status = payload.get("status", "Present")
            method = payload.get("method", "Visual Confirmation")

            # Basic Validation
            if not schedule:
                local_log(f"Check-in REJECTED: Schedule ID '{sched_id}' not found.", "error")
                conn.commit()
                conn.close()
                self.send_json_response({"success": False, "reason": "INVALID_SCHEDULE_ID"})
                return

            sched_start_h, sched_start_m = map(int, schedule["startTime"].split(":"))
            sched_end_h, sched_end_m = map(int, schedule["endTime"].split(":"))
            scan_minutes, start_minutes, end_minutes = h_parsed*60 + m_parsed, sched_start_h*60 + sched_start_m, sched_end_h*60 + sched_end_m

            if scan_minutes < (start_minutes - 15) or scan_minutes > end_minutes:
                local_log("Check-in REJECTED: Timestamp falls outside scheduled class bounds.", "error")
                conn.commit()
                conn.close()
                self.send_json_response({"success": False, "reason": "OUTSIDE_SCHEDULE_WINDOW"})
                return

            # Apply Status
            category = "success"
            msg = f"Marked {status} via {method}"

            if status == "Present":
                conn.execute("UPDATE students SET presents = presents + 1 WHERE id = ?", (sid,))
                category = "success"
            elif status == "Late":
                conn.execute("UPDATE students SET lates = lates + 1 WHERE id = ?", (sid,))
                category = "warning"
            elif status == "Absent":
                conn.execute("UPDATE students SET absents = absents + 1 WHERE id = ?", (sid,))
                category = "danger"

            local_log(f"Student {sid} marked {status}.", category)
            conn.execute("INSERT INTO logs (sender, category, message) VALUES (?, ?, ?)",
                         (student['name'], category, msg))

            duplicate_cache[dup_key] = time_string

            local_log(f"Ingested event validated. Kafka partitioned log: <code>partition_{sid}</code>.", "kafka")
            local_log(f"Attendance logged successfully. Student: {student['name']}, Status: <strong>{status}</strong>.", "success")

            if status == "LATE":
                msg = f"AttendSmart Alert: {student['name']} arrived LATE for course {schedule['courseId']} at {display_time_str}."
                cursor.execute("INSERT INTO alerts (time, sender, text) VALUES (?, ?, ?)", 
                               (display_time_str, f"Alert sent to parent ({student['parentEmail']})", msg))
                local_log(f"Automated alert dispatched to parent of {student['name']}: \"{msg}\"", "warning")

            rate = ((new_pres + new_late) / 10.0) * 100
            if rate < 75.0:
                msg = f"Attendance warning: {student['name']}'s attendance rate has dropped to {rate:.1f}%."
                cursor.execute("INSERT INTO alerts (time, sender, text) VALUES (?, ?, ?)", 
                               (display_time_str, f"Alert sent to parent ({student['parentEmail']})", msg))
                local_log(f"Automated alert dispatched to parent of {student['name']}: \"{msg}\"", "warning")

            conn.commit()
            conn.close()
            self.send_json_response({"success": True, "status": status})
            return

        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)

def run():
    init_db()
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, AttendSmartHTTPHandler)
    print(f"[Server SUCCESS] AttendSmart SQL Backend running on port {PORT}...")
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
    finally: httpd.server_close()

if __name__ == '__main__':
    run()
