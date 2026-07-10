from typing import Literal, Optional

from pydantic import BaseModel, Field


class IntentSchema(BaseModel):
    intent: Literal["schedule", "cancel", "unknown"] = Field(
        description="The user intent",
    )
    professional_id: Optional[int] = Field(
        default=None,
        description="ID of the medical professional",
    )
    professional_name: Optional[str] = Field(
        default=None,
        description="Name of the medical professional",
    )
    datetime: Optional[str] = Field(
        default=None,
        description="Appointment date and time in ISO format",
    )
    patient_name: Optional[str] = Field(
        default=None,
        description="Patient name extracted from question",
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for appointment (for scheduling)",
    )
