import unittest
from datetime import datetime, time, timedelta
from attendance_system import (
    Student,
    Schedule,
    Device,
    AttendanceRecord,
    AttendanceValidator,
    ReportGenerator
)

class TestAttendSmartSystem(unittest.TestCase):
    def setUp(self):
        # Create mockup database
        self.students = {
            "S101": Student("S101", "Alice Smith", "alice@school.edu", "parent.alice@home.com"),
            "S102": Student("S102", "Bob Jones", "bob@school.edu", "parent.bob@home.com"),
            "S103": Student("S103", "Charlie Brown", "charlie@school.edu", "parent.charlie@home.com")
        }

        # Schedule: Class starts at 09:00:00 AM and ends at 10:30:00 AM
        # Location: Center of classroom is at (37.7749, -122.4194) (San Francisco)
        self.schedules = {
            "SCH_CS101": Schedule(
                schedule_id="SCH_CS101",
                course_id="CS101",
                start_time=time(9, 0, 0),
                end_time=time(10, 30, 0),
                latitude=37.7749,
                longitude=-122.4194,
                geofence_radius_m=50.0
            )
        }

        self.devices = {
            "DEV_ROOM_101": Device("DEV_ROOM_101", is_active=True),
            "DEV_INACTIVE": Device("DEV_INACTIVE", is_active=False)
        }

        # Setup Validator
        self.validator = AttendanceValidator(
            students_db=self.students,
            schedules_db=self.schedules,
            devices_db=self.devices,
            biometric_min_score=0.85,
            late_margin_minutes=15
        )

        # Setup Report Generator
        self.reporter = ReportGenerator(students_db=self.students)

    def test_successful_validation_present(self):
        # Scan at 08:55 AM (within 15-minute buffer before start)
        scan_time = datetime(2026, 6, 8, 8, 55, 0)
        record = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_ROOM_101",
            latitude=37.77491,  # Very close to class location
            longitude=-122.41941,
            biometric_score=0.92
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertTrue(is_valid)
        self.assertEqual(validated_rec.status, "PRESENT")
        self.assertEqual(len(validated_rec.failure_reasons), 0)

    def test_successful_validation_late(self):
        # Scan at 09:16 AM (class starts at 09:00 AM, past 15-minute late margin)
        scan_time = datetime(2026, 6, 8, 9, 16, 0)
        record = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_ROOM_101",
            latitude=37.7749,
            longitude=-122.4194,
            biometric_score=0.95
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertTrue(is_valid)
        self.assertEqual(validated_rec.status, "LATE")

    def test_invalid_student(self):
        scan_time = datetime(2026, 6, 8, 8, 55, 0)
        record = AttendanceRecord(
            student_id="S999_UNKNOWN",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_ROOM_101"
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertFalse(is_valid)
        self.assertIn("INVALID_STUDENT_ID", validated_rec.failure_reasons)

    def test_unauthorized_device(self):
        scan_time = datetime(2026, 6, 8, 8, 55, 0)
        record = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_INACTIVE"
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertFalse(is_valid)
        self.assertIn("UNAUTHORIZED_DEVICE", validated_rec.failure_reasons)

    def test_duplicate_scans(self):
        scan_time_1 = datetime(2026, 6, 8, 8, 55, 0)
        record1 = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time_1,
            device_id="DEV_ROOM_101"
        )
        is_valid1, validated_rec1 = self.validator.validate_record(record1)
        self.assertTrue(is_valid1)

        # Scan 2: 30 seconds later (duplicate scan)
        scan_time_2 = scan_time_1 + timedelta(seconds=30)
        record2 = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time_2,
            device_id="DEV_ROOM_101"
        )
        is_valid2, validated_rec2 = self.validator.validate_record(record2)
        self.assertFalse(is_valid2)
        self.assertIn("DUPLICATE_SCAN_DETECTED", validated_rec2.failure_reasons)

    def test_biometric_confidence_low(self):
        scan_time = datetime(2026, 6, 8, 8, 55, 0)
        record = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_ROOM_101",
            biometric_score=0.72  # Below 0.85
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertFalse(is_valid)
        self.assertIn("BIOMETRIC_CONFIDENCE_LOW", validated_rec.failure_reasons)

    def test_geofence_violation(self):
        scan_time = datetime(2026, 6, 8, 8, 55, 0)
        # Lat/Lon far away (roughly 1.5 km away in San Francisco)
        record = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_ROOM_101",
            latitude=37.7600,
            longitude=-122.4100
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertFalse(is_valid)
        self.assertTrue(any("GEOFENCE_VIOLATION" in r for r in validated_rec.failure_reasons))

    def test_outside_time_window(self):
        # Class is 09:00 to 10:30. Allowed buffer starts at 08:45.
        # Scan at 08:40 AM (too early)
        scan_time = datetime(2026, 6, 8, 8, 40, 0)
        record = AttendanceRecord(
            student_id="S101",
            schedule_id="SCH_CS101",
            timestamp=scan_time,
            device_id="DEV_ROOM_101"
        )
        is_valid, validated_rec = self.validator.validate_record(record)
        self.assertFalse(is_valid)
        self.assertIn("OUTSIDE_CLASS_TIME_WINDOW", validated_rec.failure_reasons)

    def test_report_generation_and_warnings(self):
        # Simulate active records for a set of sessions (e.g. 10 total sessions)
        # S101 (Alice): Present 8 times, Late 1 time -> Attended 9/10 (90%) -> No warning
        # S102 (Bob): Present 5 times, Late 1 time -> Attended 6/10 (60%) -> Warning
        # S103 (Charlie): 0 records -> Attended 0/10 (0%) -> Warning

        records = []
        # S101
        for day in range(1, 9):
            records.append(AttendanceRecord(
                student_id="S101", schedule_id="SCH_CS101",
                timestamp=datetime(2026, 6, day, 8, 55, 0), device_id="DEV_ROOM_101", status="PRESENT"
            ))
        records.append(AttendanceRecord(
            student_id="S101", schedule_id="SCH_CS101",
            timestamp=datetime(2026, 6, 9, 9, 20, 0), device_id="DEV_ROOM_101", status="LATE"
        ))

        # S102
        for day in range(1, 6):
            records.append(AttendanceRecord(
                student_id="S102", schedule_id="SCH_CS101",
                timestamp=datetime(2026, 6, day, 8, 55, 0), device_id="DEV_ROOM_101", status="PRESENT"
            ))
        records.append(AttendanceRecord(
            student_id="S102", schedule_id="SCH_CS101",
            timestamp=datetime(2026, 6, 6, 9, 20, 0), device_id="DEV_ROOM_101", status="LATE"
        ))

        # Test metrics S101
        metrics_s101 = self.reporter.compile_student_metrics("S101", records, total_sessions=10)
        self.assertEqual(metrics_s101["presents"], 8)
        self.assertEqual(metrics_s101["lates"], 1)
        self.assertEqual(metrics_s101["absents"], 1)
        self.assertEqual(metrics_s101["attendance_rate"], 90.0)
        self.assertFalse(metrics_s101["alert_required"])

        # Test metrics S102
        metrics_s102 = self.reporter.compile_student_metrics("S102", records, total_sessions=10)
        self.assertEqual(metrics_s102["presents"], 5)
        self.assertEqual(metrics_s102["lates"], 1)
        self.assertEqual(metrics_s102["absents"], 4)
        self.assertEqual(metrics_s102["attendance_rate"], 60.0)
        self.assertTrue(metrics_s102["alert_required"])

        # Check low attendance warnings
        warnings = self.reporter.generate_low_attendance_warnings(records, ["SCH_CS101"], total_sessions=10)
        
        # S102 and S103 should have warnings
        warn_ids = {w["student_id"] for w in warnings}
        self.assertIn("S102", warn_ids)
        self.assertIn("S103", warn_ids)
        self.assertNotIn("S101", warn_ids)

        # Confirm length of warnings is 2
        self.assertEqual(len(warnings), 2)

if __name__ == "__main__":
    unittest.main()
