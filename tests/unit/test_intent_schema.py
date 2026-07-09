from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.intent import IntentSchema


def test_intent_schema_accepts_minimal_unknown():
    data = IntentSchema(intent="unknown")
    assert data.intent == "unknown"
    assert data.professional_id is None
    assert data.model_dump(exclude_none=True) == {"intent": "unknown"}


def test_intent_schema_accepts_full_schedule(intent_schedule: IntentSchema):
    dumped = intent_schedule.model_dump(exclude_none=True)
    assert dumped["intent"] == "schedule"
    assert dumped["professional_id"] == 1
    assert dumped["patient_name"] == "Maria Santos"


def test_intent_schema_rejects_invalid_intent():
    with pytest.raises(ValidationError):
        IntentSchema(intent="book")
