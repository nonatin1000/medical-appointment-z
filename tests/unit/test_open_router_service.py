from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.models.intent import IntentSchema
from app.services.open_router_services import OpenRouterService


def test_generate_structured_success(intent_schedule: IntentSchema):
    mock_client = MagicMock()
    structured = MagicMock()
    structured.invoke.return_value = intent_schedule
    mock_client.with_structured_output.return_value = structured

    with patch(
        "app.services.open_router_services.ChatOpenAI",
        return_value=mock_client,
    ):
        service = OpenRouterService()
        result = service.generate_structured("sys", "user", IntentSchema)

    assert result["success"] is True
    assert result["data"].intent == "schedule"
    mock_client.with_structured_output.assert_called_once_with(IntentSchema)
    structured.invoke.assert_called_once()


def test_generate_structured_failure_returns_error_dict():
    mock_client = MagicMock()
    structured = MagicMock()
    structured.invoke.side_effect = RuntimeError("boom")
    mock_client.with_structured_output.return_value = structured

    with patch(
        "app.services.open_router_services.ChatOpenAI",
        return_value=mock_client,
    ):
        service = OpenRouterService()
        result = service.generate_structured("sys", "user", IntentSchema)

    assert result["success"] is False
    assert "boom" in result["error"]
