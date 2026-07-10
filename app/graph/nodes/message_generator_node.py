from __future__ import annotations

import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage
from app.models.message import MessageSchema
from app.prompts.v1.message_generator import get_system_prompt, get_user_prompt
from app.services.open_router_service import open_router_service


logger = logging.getLogger(__name__)


def message_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a message based on the state.
    """
    logger.info("Generating message...")
    messages: List[Any] = state.get("messages", [])
    missing_fields = []

    try:
        intent = state.get("intent")
        if intent in ("schedule", "cancel"):
            if not state.get("professional_id"):
                missing_fields.append("profissional")
            if not state.get("patient_name"):
                missing_fields.append("nome do paciente")
            if not state.get("datetime"):
                missing_fields.append("data e horário")
        if missing_fields:
            reply = f"Para continuar, preciso de: {', '.join(missing_fields)}."
            return {**state, "messages": [*messages, AIMessage(content=reply)]}

        if intent in ("schedule", "cancel"):
            has_succeeded = "success" if state.get("action_success") else "error"
            scenario = f"{intent}_{has_succeeded}"
        else:
            scenario = "unknown"

        details = {
            "professional_name": state.get("professional_name"),
            "datetime": state.get("datetime"),
            "patient_name": state.get("patient_name"),
            "error": state.get("error") or state.get("action_error"),
        }
        result = open_router_service.generate_structured(
            get_system_prompt(),
            get_user_prompt(scenario, details),
            MessageSchema,
        )

        if not result["success"]:
            logger.warning("Message generation failed: %s", result["error"])
            reply = "Desculpe, não consegui gerar uma resposta agora. Tente novamente."
        else:
            reply = result["data"].message

        return {**state, "messages": [*messages, AIMessage(content=reply)]}
        
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        return {**state, "messages": [*messages, AIMessage(content=f"An error occurred while processing your request: {e}")]}