from __future__ import annotations

import logging
from typing import Any, Dict, List

from langchain_core.messages import AIMessage


logger = logging.getLogger(__name__)


def message_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a message based on the state.
    """
    logger.info("Generating message...")
    messages: List[Any] = state.get("messages", [])
    missing_fields = []

    try:
        if state.get("intent") in ("schedule", "cancel"):
            if not state.get("professional_id"):
                missing_fields.append("profissional")
            if not state.get("patient_name"):
                missing_fields.append("nome do paciente")
            if not state.get("datetime"):
                missing_fields.append("data e horário")
        if missing_fields:
            reply = f"Para continuar, preciso de: {', '.join(missing_fields)}."
            return {**state, "messages": [*messages, AIMessage(content=reply)]}
        if state.get("action_success"):
            reply = "Sua solicitação foi concluída com sucesso."
        elif state.get("action_error"):
            reply = f"Ocorreu um erro: {state['action_error']}"
        else:
            reply = "Não consegui identificar sua solicitação."
        return {**state, "messages": [*messages, AIMessage(content=reply)]}
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        return {**state, "messages": [*messages, AIMessage(content=f"An error occurred while processing your request: {e}")]}