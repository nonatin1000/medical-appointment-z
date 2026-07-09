from __future__ import annotations

from app.graph.graph import _route_by_intent


def test_route_schedule():
    assert _route_by_intent({"intent": "schedule"}) == "schedule"


def test_route_cancel():
    assert _route_by_intent({"intent": "cancel"}) == "cancel"


def test_route_unknown_goes_to_message():
    assert _route_by_intent({"intent": "unknown"}) == "message"


def test_route_error_goes_to_message():
    assert _route_by_intent({"intent": "schedule", "error": "boom"}) == "message"


def test_route_missing_intent_goes_to_message():
    assert _route_by_intent({}) == "message"
