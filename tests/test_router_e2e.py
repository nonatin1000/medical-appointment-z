from datetime import datetime, timedelta, timezone
import re
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app.main as app_main
from app.graph import graph as graph_module
import app.services.appointment_service as svc
from app.services.appointment_service import AppointmentService, professionals

app = app_main.app

client = TestClient(app)


def make_request(message: str):
    return client.post("/chat", json={"question": message, "professionals": professionals})


def _extract_patient_name(text: str) -> str | None:
    match = re.search(
        r"\b(?:sou|me chamo)\s+([A-Za-zÀ-ÿ\s]+?)(?:,| e | para |$)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).strip()


def _extract_datetime(text: str) -> str | None:
    now = datetime.now(timezone.utc)
    if "amanhã" in text:
        target_date = now.date() + timedelta(days=1)
    elif "hoje" in text:
        target_date = now.date()
    else:
        return None

    hour_match = re.search(r"(\d{1,2})h", text)
    if not hour_match:
        return None
    hour = int(hour_match.group(1))
    appt = datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=hour,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=timezone.utc,
    )
    return appt.isoformat().replace("+00:00", "Z")


def _normalize_text(text: str) -> str:
    normalized = re.sub(r"[^\w\s]", " ", text.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _contains_professional(text: str, professional_name: str) -> bool:
    normalized_text = _normalize_text(text)
    normalized_name = _normalize_text(professional_name)
    tokens = [t for t in normalized_name.split() if t not in {"dr", "dra"}]
    if tokens:
        text_tokens = set(normalized_text.split())
        token_matches = [token for token in tokens if token in text_tokens]
        if len(token_matches) >= min(2, len(tokens)):
            return True

    text_compact = re.sub(r"\s+", "", normalized_text)
    name_compact = re.sub(r"\s+", "", normalized_name)
    return bool(name_compact) and name_compact in text_compact


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch):
    svc._appointments[:] = [
        {
            "date": svc._today_at_11_utc().isoformat(),
            "patient_name": "Joao da Silva",
            "reason": "check-up regular",
            "professional_id": professionals[0]["id"],
        },
        {
            "date": svc._tomorrow_at_14_utc().isoformat(),
            "patient_name": "Luana Costa",
            "reason": "Erupção cutânea",
            "professional_id": professionals[1]["id"],
        },
    ]

    def _stub_identify_intent_node(state: dict):
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        text = getattr(last_message, "content", "") if last_message else ""
        text_lower = text.lower()

        if "agendar" in text_lower:
            intent = "schedule"
        elif "cancel" in text_lower or "cancele" in text_lower:
            intent = "cancel"
        else:
            intent = "unknown"

        data = {"intent": intent}

        available_professionals = state.get("professionals") or professionals
        for prof in available_professionals:
            if _contains_professional(text, prof["name"]):
                data["professional_id"] = prof["id"]
                data["professional_name"] = prof["name"]
                break

        patient_name = _extract_patient_name(text)
        if patient_name:
            data["patient_name"] = patient_name

        dt = _extract_datetime(text_lower)
        if dt:
            data["datetime"] = dt

        return {**state, **data}

    def _stub_generate_structured(system_prompt: str, user_prompt: str, schema):
        import json

        from app.models.message import MessageSchema

        scenario = json.loads(user_prompt)["scenario"]
        if scenario.endswith("_success"):
            message = "Sua solicitação foi concluída com sucesso."
        elif scenario.endswith("_error"):
            message = "Ocorreu um erro: não foi possível concluir sua solicitação."
        else:
            message = "Posso ajudá-lo(a) a agendar ou cancelar consultas médicas."
        return {"success": True, "data": MessageSchema(message=message)}

    llm = MagicMock()
    llm.generate_structured.side_effect = _stub_generate_structured

    monkeypatch.setattr(
        graph_module,
        "create_identify_intent_node",
        lambda _llm: _stub_identify_intent_node,
    )
    app_main.graph = graph_module.build_appointment_graph(llm, AppointmentService())
    yield


def test_schedule_appointment_success():
    message = (
        f"Olá, sou Maria Santos e quero agendar uma consulta com {professionals[0]['name']} "
        "Dr. Alicio da Silva para amanhã às 14h para um check-up regular"
    )
    response = make_request(message)

    print("Schedule Success Response:", response.text)

    assert response.status_code == 200
    body = response.json()
    assert body["messages"][0]["content"] == message
    assert body["intent"] == "schedule"
    assert body["action_success"] is True
    assert body["messages"][-1]["content"] == "Sua solicitação foi concluída com sucesso."


def test_cancel_appointment_success():
    schedule_message = (
        f"Sou Joao da Silva e quero agendar uma consulta com {professionals[1]['name']} "
        "para hoje às 14h"
    )
    make_request(schedule_message)

    cancel_message = (
        f"Cancele minha consulta com {professionals[1]['name']} que tenho hoje às 14h, me chamo Joao da Silva"
    )
    response = make_request(cancel_message)

    print("Cancel Success Response:", response.text)

    assert response.status_code == 200
    body = response.json()
    assert body["messages"][0]["content"] == cancel_message
    assert body["intent"] == "cancel"
    assert body["action_success"] is True
    assert body["messages"][-1]["content"] == "Sua solicitação foi concluída com sucesso."


def test_cancel_nonexistent_appointment():
    message = f"Cancele minha consulta com {professionals[0]['name']} hoje às 10h, me chamo Ana"
    response = make_request(message)

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "cancel"
    assert body["action_success"] is False
    assert body["action_error"]
    assert body["messages"][-1]["content"].startswith("Ocorreu um erro:")


def test_schedule_duplicate_time_fails():
    message = f"Sou Maria e quero agendar com {professionals[0]['name']} hoje às 11h para check-up"
    make_request(message)
    response = make_request(message)

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "schedule"
    assert body["action_success"] is False
    assert body["action_error"]
    assert body["messages"][-1]["content"].startswith("Ocorreu um erro:")


def test_unknown_intent_returns_message():
    message = "Qual a previsão do tempo hoje?"
    response = make_request(message)

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "unknown"
    assert body["messages"][-1]["content"]  # resposta do bot
