import pytest

from app.status import ApplicationStatus, assert_status_change_allowed


def test_user_can_mark_sent():
    assert_status_change_allowed(
        current=ApplicationStatus.READY_TO_SEND,
        new=ApplicationStatus.SENT,
        actor="user",
    )


def test_system_cannot_mark_sent():
    with pytest.raises(ValueError, match="Only the user can mark an application as sent"):
        assert_status_change_allowed(
            current=ApplicationStatus.READY_TO_SEND,
            new=ApplicationStatus.SENT,
            actor="system",
        )


def test_system_can_prepare_ready_to_send():
    assert_status_change_allowed(
        current=ApplicationStatus.DRAFT,
        new=ApplicationStatus.READY_TO_SEND,
        actor="system",
    )
