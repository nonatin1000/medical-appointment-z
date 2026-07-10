from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple, Callable

from app.models.intent import IntentSchema
from app.prompts.v1.identify_intent import USER_PROMPT_TEMPLATE, get_system_prompt
from app.services.appointment_service import professionals as default_professionals
from app.services.open_router_service import OpenRouterService

logger = logging.getLogger(__name__)


def _extract_input(state: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    """Extrai texto e profissionais do estado (API FastAPI ou LangGraph Studio)."""
    messages: List[Any] = state.get("messages", [])
    last_message = messages[-1] if messages else None

    if isinstance(last_message, dict):
        raw = last_message.get("content") or last_message.get("text") or ""
    else:
        raw = getattr(last_message, "content", "") or ""

    professionals = list(state.get("professionals") or [])

    # No Studio, o input costuma vir como JSON no content da mensagem
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                if payload.get("message"):
                    raw = payload["message"]
                if payload.get("professionals"):
                    professionals = payload["professionals"]
        except json.JSONDecodeError:
            pass

    if not professionals:
        professionals = default_professionals

    return str(raw), professionals

def create_identify_intent_node(llm_client: OpenRouterService) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Cria um nó de identificação de intent."""
    
    logger.info("Creating identify intent node...")

    def identify_intent_node(state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Identifying intent...")

        input_text, professionals = _extract_input(state)

        try:
            logger.info("Calling LLM for intent classification")
            system_prompt = get_system_prompt(professionals)
            user_prompt = USER_PROMPT_TEMPLATE.format(question=input_text)
            result = llm_client.generate_structured(
                system_prompt,
                user_prompt,
                IntentSchema,
            )
            if not result["success"]:
                return {
                    **state,
                    "professionals": professionals,
                    "intent": "unknown",
                    "error": result["error"],
                }

            data = result["data"]
            return {
                **state,
                "professionals": professionals,
                **data.model_dump(exclude_none=True),
            }

        except Exception as exc:
            logger.error("Error in identify_intent_node: %s", exc)
            return {
                **state,
                "professionals": professionals,
                "intent": "unknown",
                "error": str(exc) or "Intent identification failed",
            }

    return identify_intent_node