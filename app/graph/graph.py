from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph

from app.graph.nodes.canceller_node import create_canceller_node
from app.graph.nodes.identify_intent_node import create_identify_intent_node
from app.graph.nodes.message_generator_node import create_message_generator_node
from app.graph.nodes.scheduler_node import create_scheduler_node
from app.services.appointment_service import AppointmentService
from app.services.open_router_service import OpenRouterService

logger = logging.getLogger(__name__)


class GraphState(TypedDict, total=False):
    messages: List[BaseMessage]
    professionals: List[Dict[str, Any]]
    patient_name: Optional[str]
    intent: Optional[str]
    professional_id: Optional[int]
    professional_name: Optional[str]
    datetime: Optional[str]
    reason: Optional[str]
    action_success: Optional[bool]
    action_error: Optional[str]
    appointment_data: Optional[Any]
    error: Optional[str]


def _route_by_intent(state: Dict[str, Any]) -> str:
    if state.get("error") or not state.get("intent") or state.get("intent") == "unknown":
        return "message"

    return state["intent"]


def build_appointment_graph(
    llm_client: OpenRouterService,
    appointment_service: AppointmentService,
):
    """Cria um grafo de agendamento de consulta."""
    logger.info("Building appointment graph...")

    workflow = StateGraph(GraphState)

    workflow.add_node("identify_intent", create_identify_intent_node(llm_client))
    workflow.add_node("schedule", create_scheduler_node(appointment_service))
    workflow.add_node("cancel", create_canceller_node(appointment_service))
    workflow.add_node("message", create_message_generator_node(llm_client))

    workflow.add_edge(START, "identify_intent")
    workflow.add_conditional_edges(
        "identify_intent",
        _route_by_intent,
        {
            "schedule": "schedule",
            "cancel": "cancel",
            "message": "message",
        },
    )
    workflow.add_edge("schedule", "message")
    workflow.add_edge("cancel", "message")
    workflow.add_edge("message", END)

    return workflow.compile(name="medical-appointment-graph")
