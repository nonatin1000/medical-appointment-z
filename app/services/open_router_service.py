import logging
from typing import NotRequired, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import (
    OPENAI_BASE_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    TEMPERATURE,
)
from app.models.model_config import ModelConfig

logger = logging.getLogger(__name__)


class StructuredResult(TypedDict):
    success: bool
    data: NotRequired[BaseModel]
    error: NotRequired[str]


class OpenRouterService:
    def __init__(self, config_override: ModelConfig | None = None) -> None:
        self.config = config_override or {
            "api_key": OPENROUTER_API_KEY or "",
            "http_referer": "",
            "x_title": "medical-appointment-z",
            "models": [OPENROUTER_MODEL],
            "temperature": TEMPERATURE,
        }
        self.llm_client = ChatOpenAI(
            api_key=self.config["api_key"],
            model=self.config["models"][0],
            temperature=self.config["temperature"],
            base_url=OPENAI_BASE_URL,
            default_headers={
                "HTTP-Referer": self.config["http_referer"],
                "X-Title": self.config["x_title"],
            },
        )

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> StructuredResult:
        try:
            llm = self.llm_client.with_structured_output(schema)
            data = llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ],
                config={"run_name": "generate_structured"},
            )
            return {"success": True, "data": data}
        except Exception:
            logger.exception("Error generating structured output")
            return {
                "success": False,
                "error": "structured_output_generation_failed",
            }

open_router_service = OpenRouterService()
