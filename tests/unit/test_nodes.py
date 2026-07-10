from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from app.graph.nodes.canceller_node import canceller_node
from app.graph.nodes.identify_intent_node import identify_intent_node
from app.graph.nodes.message_generator_node import message_generator_node
from app.graph.nodes.scheduler_node import scheduler_node
from app.models.intent import IntentSchema
from app.models.message import MessageSchema
from app.services.appointment_service import professionals


def test_identify_intent_node_success(intent_schedule: IntentSchema, sample_professionals: list[dict]):
    state = {
        "messages": [HumanMessage(content="quero agendar")],
        "professionals": sample_professionals,
    }
    mock_result = {"success": True, "data": intent_schedule}

    with patch(
        "app.graph.nodes.identify_intent_node.open_router_service.generate_structured",
        return_value=mock_result,
    ):
        result = identify_intent_node(state)

    assert result["intent"] == "schedule"
    assert result["professional_id"] == 1
    assert result["patient_name"] == "Maria Santos"
    assert result["professionals"] == sample_professionals


def test_identify_intent_node_llm_failure(sample_professionals: list[dict]):
    state = {
        "messages": [HumanMessage(content="oi")],
        "professionals": sample_professionals,
    }

    with patch(
        "app.graph.nodes.identify_intent_node.open_router_service.generate_structured",
        return_value={"success": False, "error": "llm down"},
    ):
        result = identify_intent_node(state)

    assert result["intent"] == "unknown"
    assert result["error"] == "llm down"


def test_identify_intent_parses_studio_json_payload(intent_schedule: IntentSchema):
    payload = (
        '{"message":"quero agendar com Alicio",'
        '"professionals":[{"id":1,"name":"Dr. Alicio da Silva","specialty":"Cardiologia"}]}'
    )
    state = {"messages": [HumanMessage(content=payload)]}

    with patch(
        "app.graph.nodes.identify_intent_node.open_router_service.generate_structured",
        return_value={"success": True, "data": intent_schedule},
    ) as mock_generate:
        result = identify_intent_node(state)

    assert result["intent"] == "schedule"
    user_prompt = mock_generate.call_args.args[1]
    assert "quero agendar com Alicio" in user_prompt


def test_scheduler_node_success(free_slot):
    state = {
        "professional_id": professionals[0]["id"],
        "patient_name": "Maria Santos",
        "datetime": free_slot.isoformat().replace("+00:00", "Z"),
        "reason": "check-up",
    }
    result = scheduler_node(state)
    assert result["action_success"] is True
    assert result["appointment_data"]["patient_name"] == "Maria Santos"


def test_scheduler_node_missing_fields():
    result = scheduler_node({"professional_id": 1})
    assert result["action_success"] is False
    assert "Appointment datetime is required" in result["action_error"]
    assert "Patient name is required" in result["action_error"]


def test_scheduler_node_uses_default_reason(free_slot):
    state = {
        "professional_id": professionals[0]["id"],
        "patient_name": "Maria Santos",
        "datetime": free_slot.isoformat().replace("+00:00", "Z"),
    }
    result = scheduler_node(state)
    assert result["action_success"] is True
    assert result["appointment_data"]["reason"] == "general consultation"


def test_canceller_node_success():
    # seed: Joao + Alicio today 11h
    from app.services import appointment_service as svc

    state = {
        "professional_id": professionals[0]["id"],
        "patient_name": "Joao da Silva",
        "datetime": svc._today_at_11_utc().isoformat().replace("+00:00", "Z"),
    }
    result = canceller_node(state)
    assert result["action_success"] is True


def test_canceller_node_not_found(free_slot):
    state = {
        "professional_id": professionals[0]["id"],
        "patient_name": "Maria",
        "datetime": free_slot.isoformat().replace("+00:00", "Z"),
    }
    result = canceller_node(state)
    assert result["action_success"] is False
    assert "Appointment not found" in result["action_error"]


def test_canceller_node_wrong_patient_cannot_cancel():
    from app.services import appointment_service as svc

    state = {
        "professional_id": professionals[0]["id"],
        "patient_name": "Outra Pessoa",
        "datetime": svc._today_at_11_utc().isoformat().replace("+00:00", "Z"),
    }
    result = canceller_node(state)
    assert result["action_success"] is False
    assert "Appointment not found" in result["action_error"]


def test_canceller_node_missing_fields():
    result = canceller_node({"patient_name": "Maria"})
    assert result["action_success"] is False
    assert "Professional ID is required" in result["action_error"]
    assert "Appointment datetime is required" in result["action_error"]


def test_message_generator_success():
    state = {
        "messages": [HumanMessage(content="oi")],
        "intent": "schedule",
        "professional_id": 1,
        "professional_name": "Dr. Alicio da Silva",
        "patient_name": "Maria Santos",
        "datetime": "2026-07-11T14:00:00Z",
        "action_success": True,
    }
    mock_result = {"success": True, "data": MessageSchema(message="Sua consulta foi agendada com sucesso!")}

    with patch(
        "app.graph.nodes.message_generator_node.open_router_service.generate_structured",
        return_value=mock_result,
    ) as mock_generate:
        result = message_generator_node(state)

    assert isinstance(result["messages"][-1], AIMessage)
    assert result["messages"][-1].content == "Sua consulta foi agendada com sucesso!"
    user_prompt = mock_generate.call_args.args[1]
    assert "schedule_success" in user_prompt
    assert "Maria Santos" in user_prompt


def test_message_generator_missing_fields():
    state = {
        "messages": [],
        "intent": "schedule",
        "patient_name": "Maria",
    }
    result = message_generator_node(state)
    content = result["messages"][-1].content
    assert "profissional" in content
    assert "data e horário" in content


def test_message_generator_action_error():
    state = {
        "messages": [],
        "intent": "cancel",
        "professional_id": 1,
        "patient_name": "Joao",
        "datetime": "2026-07-09T11:00:00Z",
        "action_error": "Appointment not found",
    }
    mock_result = {"success": True, "data": MessageSchema(message="Não encontrei sua consulta, Joao.")}

    with patch(
        "app.graph.nodes.message_generator_node.open_router_service.generate_structured",
        return_value=mock_result,
    ) as mock_generate:
        result = message_generator_node(state)

    assert result["messages"][-1].content == "Não encontrei sua consulta, Joao."
    user_prompt = mock_generate.call_args.args[1]
    assert "cancel_error" in user_prompt
    assert "Appointment not found" in user_prompt


def test_message_generator_llm_failure():
    state = {
        "messages": [],
        "intent": "unknown",
    }

    with patch(
        "app.graph.nodes.message_generator_node.open_router_service.generate_structured",
        return_value={"success": False, "error": "llm down"},
    ):
        result = message_generator_node(state)

    assert "não consegui gerar uma resposta" in result["messages"][-1].content
