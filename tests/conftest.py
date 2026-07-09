from __future__ import annotations

from datetime import datetime, timezone

import pytest

import app.services.appointment_service as appointment_module
from app.models.intent import IntentSchema
from app.services.appointment_service import AppointmentService, professionals


@pytest.fixture
def sample_professionals() -> list[dict]:
    return list(professionals)


@pytest.fixture
def appointment_service() -> AppointmentService:
    return AppointmentService()


@pytest.fixture(autouse=True)
def reset_appointments():
    """Garante estado em memoria limpo e deterministico entre testes."""
    appointment_module._appointments[:] = [
        {
            "date": appointment_module._today_at_11_utc().isoformat(),
            "patient_name": "Joao da Silva",
            "reason": "check-up regular",
            "professional_id": professionals[0]["id"],
        },
        {
            "date": appointment_module._tomorrow_at_14_utc().isoformat(),
            "patient_name": "Luana Costa",
            "reason": "Erupção cutânea",
            "professional_id": professionals[1]["id"],
        },
    ]
    yield


@pytest.fixture
def free_slot() -> datetime:
    return datetime(2026, 7, 15, 16, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def intent_schedule() -> IntentSchema:
    return IntentSchema(
        intent="schedule",
        professional_id=1,
        professional_name="Dr. Alicio da Silva",
        datetime="2026-07-15T16:00:00.000Z",
        patient_name="Maria Santos",
        reason="check-up",
    )
