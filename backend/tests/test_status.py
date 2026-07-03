import pytest
from pydantic import ValidationError
from sqlalchemy import exc, text
from sqlmodel import Session, SQLModel, create_engine

from app.models import Vacancy
from app.schemas import StatusUpdate, VacancyCreate, VacancyRead
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


def test_vacancy_status_persists_human_value():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Vacancy(external_id="vacancy-1"))
        session.commit()

    with engine.connect() as connection:
        stored_status = connection.execute(
            text("SELECT submit_status FROM vacancy WHERE external_id = :external_id"),
            {"external_id": "vacancy-1"},
        ).scalar_one()

    assert stored_status == ApplicationStatus.DRAFT.value


def test_invalid_vacancy_status_string_is_rejected_on_persistence():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Vacancy(external_id="vacancy-1", submit_status="Bogus"))

        with pytest.raises(exc.StatementError):
            session.commit()


def test_vacancy_status_round_trips_as_enum_and_value():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        vacancy = Vacancy(external_id="vacancy-1", submit_status=ApplicationStatus.SENT)
        session.add(vacancy)
        session.commit()
        vacancy_id = vacancy.id
        session.expunge_all()

        reloaded = session.get(Vacancy, vacancy_id)

    assert reloaded is not None
    assert reloaded.submit_status == ApplicationStatus.SENT

    with engine.connect() as connection:
        stored_status = connection.execute(
            text("SELECT submit_status FROM vacancy WHERE external_id = :external_id"),
            {"external_id": "vacancy-1"},
        ).scalar_one()

    assert stored_status == ApplicationStatus.SENT.value


def test_status_update_rejects_actor():
    with pytest.raises(ValidationError):
        StatusUpdate(status=ApplicationStatus.READY_TO_SEND, actor="system")


def test_vacancy_create_rejects_description_without_model_field():
    with pytest.raises(ValidationError):
        VacancyCreate(
            external_id="vacancy-1",
            company="Example Co",
            title="Operations Manager",
            description="No matching field exists on the model.",
        )


def test_vacancy_read_validates_from_model_attributes():
    vacancy = Vacancy(
        id=1,
        external_id="vacancy-1",
        company="Example Co",
        title="Operations Manager",
    )

    assert VacancyRead.model_validate(vacancy).external_id == "vacancy-1"
