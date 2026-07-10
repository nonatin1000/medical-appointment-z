from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Dict
from app.services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = {
    "professional_id": "Professional ID is required",
    "datetime": "Appointment datetime is required",
    "patient_name": "Patient name is required",
}


def canceller_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cancel an appointment.
    """
    logger.info("Cancelling appointment...")
    service = AppointmentService()
    try:
        errors = [message for field, message in _REQUIRED_FIELDS.items() if not state.get(field)]
        if errors:
            error_messages = ", ".join(errors)
            logger.warning("Validation failed: %s", error_messages)
            return {**state, "action_success": False, "action_error": error_messages}

        appt_date = datetime.fromisoformat(state["datetime"].replace("Z", "+00:00"))
        service.cancel_appointment(
            professional_id=int(state["professional_id"]),
            patient_name=state["patient_name"],
            date=appt_date,
        )
        logger.info("Appointment cancelled successfully")
        return {**state, "action_success": True}
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return {
            **state,
            "action_success": False,
            "action_error": str(e) or "Cancellation failed",
        }