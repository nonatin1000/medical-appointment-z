from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENROUTER_MODEL, TEMPERATURE
from app.prompts.v1.identify_intent import USER_PROMPT_TEMPLATE, get_system_prompt
from app.services.appointment_service import professionals as default_professionals

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


def identify_intent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Identifying intent...")

    input_text, professionals = _extract_input(state)

    try:
        logger.info("Calling LLM for intent classification")
        llm = ChatOpenAI(
            model=OPENROUTER_MODEL,
            temperature=TEMPERATURE,
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
        system_prompt = get_system_prompt(professionals)
        user_prompt = USER_PROMPT_TEMPLATE.format(question=input_text)
        user_prompt = f"{user_prompt}\nResponda em JSON válido."

        response = llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)],
            config={"run_name": "identify_intent"},
        )
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response.content, re.DOTALL)
            if not match:
                raise
            data = json.loads(match.group(0))

        return {
            **state,
            "professionals": professionals,
            **data,
        }

    except Exception as exc:
        logger.error(f"Error in identify_intent_node: {exc}")
        return {
            **state,
            "professionals": professionals,
            "intent": "unknown",
            "error": str(exc) or "Intent identification failed",
        }
