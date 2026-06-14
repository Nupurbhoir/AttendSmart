# AttendSmart: Enterprise Cloud Attendance System
## Final Project Documentation

### 1. Problem Statement
Traditional attendance systems in educational institutions rely heavily on manual roll-call or basic RFID card scanning, leading to proxy attendance, time wastage, and lack of real-time analytics. There is a critical need for an automated, secure, and highly scalable attendance mechanism that handles data from millions of students across campuses using multiple ingestion methods (Biometrics, RFID, Manual Faculty Portal).

### 2. Proposed Solution
**AttendSmart** is a next-generation cloud-based attendance system that solves these challenges by implementing a distributed event-driven architecture:
1. **Multi-Modal Validation:** Ingests raw scans from Biometric hardware, RFID readers, and an interactive **Faculty Manual Web Portal**.
2. **Centralized Synchronization:** Validates timestamps against scheduled class bounds and uses high-speed caching to prevent duplicate/proxy scans in real-time.
Only when conditions are met is the attendance marked as compliant and saved across the cluster.

### 3. System Architecture
The system follows a monolithic client-server architecture with a clear separation of concerns.
- **Client Tier:** HTML/Vanilla JS web application that acts as both the administrative dashboard and the hardware simulator.
- **Application Tier:** Python REST API gateway that processes check-in requests, executes geofence validation algorithms, and handles JWT authentication.
- **Data Tier:** SQLite Relational Database providing persistent storage for student profiles, device logs, and system alerts.

### 4. Module Description
- **Simulator Module (`simulator.html`):** Emulates hardware terminal functionality. Ingests raw biometric scores and GPS coordinates and dispatches them to the backend API.
- **Dashboard Module (`dashboard.html`):** Administrative control panel providing real-time visibility into attendance metrics, live event streams, and CSV report generation.
- **API Gateway (`server.py`):** The core routing engine that intercepts HTTP requests, enforces security rules, and performs CRUD operations.
- **Analytics Engine:** Processes database records to classify attendance into "Compliant", "Low Attendance", or "Severe Drop" categories automatically.

### 5. Database Design
The system utilizes a relational SQLite database (`attendance.db`) composed of three primary tables:
- `students`: Stores student metadata (ID, Name, Email, Avatar, Active Status, Present Count, Late Count, Absent Count).
- `devices`: Stores registered hardware terminal data (Terminal ID, Location Name, Coordinates, Status).
- `logs`: An immutable ledger recording every check-in attempt (Timestamp, Student ID, Category, Outcome Message).
- `alerts`: Stores system-generated notifications for admins and parents.

### 6. Technology Stack
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript (ES6+), FontAwesome Icons, Google Fonts.
- **Backend:** Python 3 (Native `http.server` library - No external frameworks).
- **Database:** SQLite3 (Relational SQL Database).
- **Architecture:** RESTful JSON APIs.

### 7. Implementation Details
The core logic resides in the `/api/checkin` endpoint. When a POST request is received:
1. The payload is parsed to extract `studentId`, `deviceId`, `status`, and `method`.
2. A duplicate check occurs to ensure the student hasn't already been checked in for this session recently.
3. The system verifies if the scan timestamp falls within the schedule's active bounds.
4. If successful, SQL `UPDATE` and `INSERT` commands execute to update the student's metrics based on their `status` (Present/Late/Absent) and log the event.

### 8. Screenshots
*(Note: Please paste your screenshots of the following pages here before generating the PDF)*
- **Landing Page (`home.html`)**
- **Admin Dashboard (`dashboard.html`)**
- **Hardware Simulator (`simulator.html`)**
- **Database Table View (via SQLite Viewer)**

### 9. Future Scope
- **Facial Recognition Integration:** Upgrading the biometric simulator to use real camera feeds via WebRTC and OpenCV.
- **Push Notifications:** Integrating Firebase Cloud Messaging (FCM) to send instant push alerts to parent mobile apps.
- **Machine Learning Analytics:** Predicting student dropout rates based on historical attendance degradation patterns.
