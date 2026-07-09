from __future__ import annotations

from datetime import datetime, timezone

import pytest

import app.services.appointment_service as appointment_module
from app.services.appointment_service import AppointmentService, professionals


def test_get_appointment_returns_seeded_appointment(appointment_service: AppointmentService):
    dt = appointment_module._today_at_11_utc()
    found = appointment_service.get_appointment(professionals[0]["id"], dt)

    assert found is not None
    assert found.patient_name == "Joao da Silva"
    assert found.professional_id == professionals[0]["id"]


def test_get_appointment_returns_none_when_missing(appointment_service: AppointmentService, free_slot: datetime):
    found = appointment_service.get_appointment(professionals[0]["id"], free_slot)
    assert found is None


def test_check_availability_true_for_free_slot(appointment_service: AppointmentService, free_slot: datetime):
    assert appointment_service.check_availability(professionals[0]["id"], free_slot) is True


def test_check_availability_false_for_booked_slot(appointment_service: AppointmentService):
    dt = appointment_module._today_at_11_utc()
    assert appointment_service.check_availability(professionals[0]["id"], dt) is False


def test_book_appointment_success(appointment_service: AppointmentService, free_slot: datetime):
    booked = appointment_service.book_appointment(
        professional_id=professionals[0]["id"],
        date=free_slot,
        patient_name="Maria Santos",
        reason="check-up",
    )

    assert booked["patient_name"] == "Maria Santos"
    assert booked["professional_id"] == professionals[0]["id"]
    assert booked["date"] == free_slot.isoformat()
    assert appointment_service.check_availability(professionals[0]["id"], free_slot) is False


def test_book_appointment_raises_when_unavailable(appointment_service: AppointmentService):
    dt = appointment_module._today_at_11_utc()
    with pytest.raises(ValueError, match="Appointment not available"):
        appointment_service.book_appointment(
            professional_id=professionals[0]["id"],
            date=dt,
            patient_name="Outra Pessoa",
            reason="consulta",
        )


def test_cancel_appointment_success(appointment_service: AppointmentService):
    dt = appointment_module._today_at_11_utc()
    assert appointment_service.cancel_appointment(professionals[0]["id"], dt) is True
    assert appointment_service.get_appointment(professionals[0]["id"], dt) is None


def test_cancel_appointment_raises_when_not_found(appointment_service: AppointmentService, free_slot: datetime):
    with pytest.raises(ValueError, match="Appointment not found"):
        appointment_service.cancel_appointment(professionals[0]["id"], free_slot)
