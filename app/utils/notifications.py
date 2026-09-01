"""
Simulated background notification and activity logging utilities.
"""

from datetime import datetime
from pathlib import Path
import time


# Store log files in the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ACTIVITY_LOG = PROJECT_ROOT / "activity_log.txt"
NOTIFICATION_LOG = PROJECT_ROOT / "notification_log.txt"


def log_activity(user_id: int, action: str):
    """
    Write a user activity entry to activity_log.txt.
    """

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    with ACTIVITY_LOG.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"[{timestamp}] "
            f"User {user_id}: {action}\n"
        )


def send_notification(
    email: str,
    message: str,
):
    """
    Simulate sending a notification.

    The 2-second delay represents a slower operation such
    as sending an email through an external service.
    """

    time.sleep(2)

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    with NOTIFICATION_LOG.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            f"[{timestamp}] "
            f"To: {email} | "
            f"Message: {message}\n"
        )