import math
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Set, Tuple

# Domain Models
class Student:
    def __init__(self, student_id: str, name: str, email: str, parent_email: str):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.parent_email = parent_email

class Schedule:
    def __init__(
        self,
        schedule_id: str,
        course_id: str,
        start_time: time,  # e.g. 09:00:00
        end_time: time,    # e.g. 10:30:00
        latitude: float,
        longitude: float,
        geofence_radius_m: float = 50.0
    ):
        self.schedule_id = schedule_id
        self.course_id = course_id
        self.start_time = start_time
        self.end_time = end_time
        self.latitude = latitude
        self.longitude = longitude
        self.geofence_radius_m = geofence_radius_m

class Device:
    def __init__(self, device_id: str, is_active: bool = True):
        self.device_id = device_id
        self.is_active = is_active

class AttendanceRecord:
    def __init__(
        self,
        student_id: str,
        schedule_id: str,
        timestamp: datetime,
        device_id: str,
        status: str = "PRESENT",  # PRESENT, LATE, ABSENT
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        biometric_score: Optional[float] = None,  # Similarity confidence (0.0 to 1.0)
        failure_reasons: Optional[List[str]] = None
    ):
        self.student_id = student_id
        self.schedule_id = schedule_id
        self.timestamp = timestamp
        self.device_id = device_id
        self.status = status
        self.latitude = latitude
        self.longitude = longitude
        self.biometric_score = biometric_score
        self.failure_reasons = failure_reasons or []

    def __repr__(self):
        return (f"AttendanceRecord(student_id={self.student_id}, schedule_id={self.schedule_id}, "
                f"status={self.status}, timestamp={self.timestamp}, failure_reasons={self.failure_reasons})")


class AttendanceValidator:
    """
    Handles validation rules for incoming attendance logs to prevent fraud,
    handling duplicates, late submissions, and geofencing mismatches.
    """
    def __init__(
        self,
        students_db: Dict[str, Student],
        schedules_db: Dict[str, Schedule],
        devices_db: Dict[str, Device],
        biometric_min_score: float = 0.85,
        late_margin_minutes: int = 15
    ):
        self.students_db = students_db
        self.schedules_db = schedules_db
        self.devices_db = devices_db
        self.biometric_min_score = biometric_min_score
        self.late_margin_minutes = late_margin_minutes
        # In-memory "cache" for duplicate check: maps (student_id, schedule_id) -> last scan timestamp
        self.duplicate_cache: Dict[Tuple[str, str], datetime] = {}

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates distance in meters between two GPS coordinates using the Haversine formula.
        """
        R = 6371000.0  # Earth's radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def validate_record(self, record: AttendanceRecord) -> Tuple[bool, AttendanceRecord]:
        """
        Runs validation checklist. If valid, assigns status (PRESENT / LATE).
        Returns a tuple of (is_valid, updated_record).
        """
        # Rule 1: Student Existence Check
        if record.student_id not in self.students_db:
            record.failure_reasons.append("INVALID_STUDENT_ID")
            return False, record

        # Rule 2: Schedule Check
        if record.schedule_id not in self.schedules_db:
            record.failure_reasons.append("INVALID_SCHEDULE_ID")
            return False, record
        schedule = self.schedules_db[record.schedule_id]

        # Rule 3: Authorized Edge Device Check
        if record.device_id not in self.devices_db or not self.devices_db[record.device_id].is_active:
            record.failure_reasons.append("UNAUTHORIZED_DEVICE")
            return False, record

        # Rule 4: Anti-Duplicate Validation (Check temporal overlap)
        cache_key = (record.student_id, record.schedule_id)
        if cache_key in self.duplicate_cache:
            last_scan_time = self.duplicate_cache[cache_key]
            # If student scanned twice within 60 seconds, flag as duplicate scan
            if (record.timestamp - last_scan_time).total_seconds() < 60:
                record.failure_reasons.append("DUPLICATE_SCAN_DETECTED")
                return False, record

        # Rule 5: Biometric Verification Score Check
        if record.biometric_score is not None:
            if record.biometric_score < self.biometric_min_score:
                record.failure_reasons.append("BIOMETRIC_CONFIDENCE_LOW")
                return False, record

        # Rule 6: Geofencing Coordinates Check (if locations are provided)
        if record.latitude is not None and record.longitude is not None:
            distance = self._haversine_distance(
                record.latitude, record.longitude,
                schedule.latitude, schedule.longitude
            )
            if distance > schedule.geofence_radius_m:
                record.failure_reasons.append(f"GEOFENCE_VIOLATION: {distance:.1f}m outer boundary")
                return False, record

        # Rule 7: Temporal Schedule Matching (Allow marking within class duration)
        scan_time_only = record.timestamp.time()
        
        # Parse boundaries
        start_dt = datetime.combine(record.timestamp.date(), schedule.start_time)
        end_dt = datetime.combine(record.timestamp.date(), schedule.end_time)
        
        # Buffer: allow scans up to 15 minutes before class starts and up to end of class
        check_start_boundary = start_dt - timedelta(minutes=15)
        
        if not (check_start_boundary <= record.timestamp <= end_dt):
            record.failure_reasons.append("OUTSIDE_CLASS_TIME_WINDOW")
            return False, record

        # Classify Status: Present vs Late
        late_cutoff = start_dt + timedelta(minutes=self.late_margin_minutes)
        if record.timestamp > late_cutoff:
            record.status = "LATE"
        else:
            record.status = "PRESENT"

        # Update cache on successful validation
        self.duplicate_cache[cache_key] = record.timestamp
        return True, record


class ReportGenerator:
    """
    Aggregates database logs to compile attendance reports and
    flags warning conditions for students falling below compliance thresholds.
    """
    def __init__(self, students_db: Dict[str, Student]):
        self.students_db = students_db

    def compile_student_metrics(
        self,
        student_id: str,
        validated_records: List[AttendanceRecord],
        total_sessions: int
    ) -> Dict:
        """
        Calculates totals and percentages for a single student.
        """
        student = self.students_db.get(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found in database.")

        # Filter records belonging to the student
        student_records = [r for r in validated_records if r.student_id == student_id]
        
        presents = sum(1 for r in student_records if r.status == "PRESENT")
        lates = sum(1 for r in student_records if r.status == "LATE")
        absents = total_sessions - (presents + lates)

        # Calculate score (Lates can count as partial attendance in some systems, here we treat Late as present for ratio)
        attended = presents + lates
        attendance_rate = (attended / total_sessions) * 100 if total_sessions > 0 else 0.0

        return {
            "student_id": student_id,
            "student_name": student.name,
            "email": student.email,
            "parent_email": student.parent_email,
            "presents": presents,
            "lates": lates,
            "absents": absents,
            "attendance_rate": round(attendance_rate, 2),
            "alert_required": attendance_rate < 75.0
        }

    def generate_low_attendance_warnings(
        self,
        validated_records: List[AttendanceRecord],
        course_schedules: List[str],  # List of schedule_ids representing expected sessions
        total_sessions: int,
        threshold_pct: float = 75.0
    ) -> List[Dict]:
        """
        Identifies all students who fall below the compliance threshold.
        """
        warnings = []
        for student_id in self.students_db.keys():
            metrics = self.compile_student_metrics(student_id, validated_records, total_sessions)
            if metrics["attendance_rate"] < threshold_pct:
                warnings.append({
                    "student_id": student_id,
                    "student_name": metrics["student_name"],
                    "parent_email": metrics["parent_email"],
                    "attendance_rate": metrics["attendance_rate"],
                    "warning_message": (
                        f"ALERT: Attendance for {metrics['student_name']} has fallen to "
                        f"{metrics['attendance_rate']}%, which is below the mandatory {threshold_pct}% threshold."
                    )
                })
        return warnings
