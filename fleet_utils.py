# fleet_utils.py
# Shared helpers for the nightly fleet run.
#
# 2026 cleanup: this was a catch-all since 2013 and most of it had no callers. The unused
# helpers (format_percent, mean, is_due, parse_service_date, chunk_list) were deleted --
# is_due in particular was a second, competing copy of km_wachter.needs_service, which is
# exactly the kind of duplicate that lets two answers to the same question drift apart.

MILES_PER_KM = 0.621371                 # 1 km = 0.621371 miles (was 1.609, which is km-per-mile)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles.

    Used by the nightly run for the UK partner report.
    """
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"
