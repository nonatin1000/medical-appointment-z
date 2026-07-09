from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Dict
from app.services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)


def canceller_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cancel an appointment.
    """
    logger.info("Cancelling appointment...")
    service = AppointmentService()
    required_fields = ["professional_id", "patient_name", "datetime"]
    try:
        if any(not state.get(field) for field in required_fields):
            return {**state, "action_success": False}
        appt_date = datetime.fromisoformat(state["datetime"].replace("Z", "+00:00"))
        appointment = service.cancel_appointment(
            professional_id=int(state.get("professional_id", 0)),
            date=appt_date,
        )
        state["appointment"] = appointment
        logger.info("Appointment cancelled successfully")
        return {**state, "action_success": True, }
    except Exception as e:
        logger.error(f"Error cancelling appointment: {e}")
        return {
            **state,
            "action_success": False,
            "action_error": str(e) or "Cancellation failed",
        }