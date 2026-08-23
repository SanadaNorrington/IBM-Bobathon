# log_util.py
# A small homemade logger, kept because the nightly run writes its own report file.
#
# 2026 cleanup: debug() and the DEBUG flag were deleted -- DEBUG had been False since 2014,
# so the branch had been dead for a decade and nothing called it.

import time

LOG_LINES: list[str] = []               # module-level buffer, shared by every importer


def log(message: str) -> None:
    """Append a timestamped message to the in-memory buffer and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Append every buffered line to the file at path, then clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
