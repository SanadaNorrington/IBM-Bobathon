# config_loader.py
# Liest settings.cfg. Selbst geschrieben, weil uns ConfigParser 2013 "zu kompliziert" war.
# (Reads settings.cfg. Hand-rolled, because ConfigParser felt "too complicated" in 2013.)

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str | None = None) -> dict:
    """Read settings.cfg and return a dict of recognised key/value pairs.

    Unknown keys are silently ignored (a typo in the cfg file will never surface).
    All values are stored as strings; callers convert as needed.
    """
    if path is None:
        path = SETTINGS_FILE
    settings: dict = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            # Broken/unknown line? Just carry on.
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return an integer setting, or fallback if the key is absent or not numeric."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return the string value for key, or fallback when the key is absent.

    (A duplicate of dict.get — was already redundant in 2013.)
    """
    return settings.get(key, fallback)
