# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernised 2026.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return how much of the service interval has been used, as a percentage."""
    return (km_since_service / interval) * 100


def has_reading(car: dict) -> bool:
    """Return True when the car has a recorded last-service odometer reading."""
    return "last_service_km" in car


def service_baseline(car: dict) -> float:
    """Return the odometer reading the current service window is measured from.

    A car with no 'last_service_km' is treated as freshly serviced, so a missing
    reading can never raise a false alert.

    Be aware of the trade-off: such a car also can never be flagged, so a missing
    reading hides a car instead of alarming about it. fleet_report counts these
    cars and prints the count, so they stay visible to the team.
    """
    return car.get("last_service_km", car["odometer"])


def needs_service(car: dict) -> bool:
    """Return True when the car has used 80% or more of its service interval."""
    km_since = car["odometer"] - service_baseline(car)
    return wear_percent(km_since, SERVICE_INTERVAL_KM) >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Return the IDs of every car that needs service and print each one."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
