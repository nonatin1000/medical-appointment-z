from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph

from app.graph.nodes.canceller_node import canceller_node
from app.graph.nodes.identify_intent_node import identify_intent_node
from app.graph.nodes.message_generator_node import message_generator_node
from app.graph.nodes.scheduler_node import scheduler_node


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


def build_appointment_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("identify_intent", identify_intent_node)
    workflow.add_node("schedule", scheduler_node)
    workflow.add_node("cancel", canceller_node)
    workflow.add_node("message", message_generator_node)

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


# Export usado pelo LangGraph Studio (`langgraph.json`)
graph = build_appointment_graph()
