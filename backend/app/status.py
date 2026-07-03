from enum import Enum


class ApplicationStatus(str, Enum):
    DRAFT = "Draft"
    READY_TO_SEND = "Ready to send"
    SENT = "Sent"
    FOLLOW_UP = "Follow-up"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


def assert_status_change_allowed(
    current: ApplicationStatus,
    new: ApplicationStatus,
    actor: str,
) -> None:
    if new == ApplicationStatus.SENT and actor != "user":
        raise ValueError("Only the user can mark an application as sent")
    if current == ApplicationStatus.ARCHIVED and new == ApplicationStatus.SENT:
        raise ValueError("Archived applications must be restored before marking sent")
