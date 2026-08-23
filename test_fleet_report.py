# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_does_not_crash_on_missing_last_service_km():
    # A car with no "last_service_km" key must not raise a KeyError.
    # VOS-7788 has only an odometer reading; the fleet summary must handle it gracefully.
    fleet = [{"id": "VOS-7788", "odometer": 92000}]
    result = fleet_summary(fleet)
    assert result["count"] == 1
    # A car with no last-service reading is treated as freshly serviced, so 0% wear.
    assert result["due"] == 0
    assert result["average_wear"] == 0.0


def test_summary_counts_cars_with_no_reading():
    # A car with no reading scores 0% wear and can never be flagged, so the summary
    # has to report it separately -- otherwise it silently vanishes from the report.
    fleet = [
        {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
        {"id": "VOS-7788", "odometer": 92000},
    ]
    assert fleet_summary(fleet)["missing_readings"] == 1
    assert fleet_summary(SAMPLE)["missing_readings"] == 0


def test_summary_handles_an_empty_fleet():
    # A nightly run against an empty fleet must not divide by zero.
    assert fleet_summary([]) == {
        "count": 0,
        "due": 0,
        "average_wear": 0.0,
        "missing_readings": 0,
    }
