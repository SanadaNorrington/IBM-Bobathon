# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Runs every morning. Modernised 2026.

import fleet_utils
from config_loader import get_setting, load_settings
from km_wachter import (
    SERVICE_INTERVAL_KM,
    has_reading,
    needs_service,
    service_baseline,
    wear_percent,
)
from log_util import flush_log, log


def car_wear(car: dict) -> float:
    """Return the wear percentage for a single car.

    Uses the same missing-reading policy as needs_service(), via the shared
    service_baseline() helper, so the two can never drift apart.
    """
    return wear_percent(car["odometer"] - service_baseline(car), SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict:
    """Return count, number due for service, average wear, and missing-reading count.

    'missing_readings' counts cars with no last-service odometer value. Those cars
    report 0% wear and are never flagged, so the count is what stops them from
    quietly disappearing out of the report.
    """
    total = 0.0
    due = 0
    missing = 0
    for car in fleet:
        total += car_wear(car)
        if needs_service(car):
            due += 1
        if not has_reading(car):
            missing += 1
    average = total / len(fleet) if fleet else 0.0
    return {
        "count": len(fleet),
        "due": due,
        "average_wear": average,
        "missing_readings": missing,
    }


def print_report(fleet: list[dict]) -> None:
    """Print the nightly fleet health report and append it to the log file."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    if s["missing_readings"]:
        # These cars count as 0% worn, so they can never trip the 80% rule.
        # Say so out loud rather than letting them vanish from the report.
        print(f"WARNING: {s['missing_readings']} car(s) have no last-service reading "
              f"and cannot be assessed - chase the missing odometer values.")
    total_km = sum(car["odometer"] for car in fleet)
    # Die Partnerwerkstatt in England will die Distanz in Meilen (seit 2015).
    # (The partner garage in England wants the distance in miles, since 2015.)
    miles = fleet_utils.km_to_miles(total_km)
    print(f"Fleet distance: {fleet_utils.format_number(miles)} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))
