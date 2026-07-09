from typing import Literal, Optional

from pydantic import BaseModel


class IntentSchema(BaseModel):
    intent: Literal["schedule", "cancel", "unknown"]
    professional_id: Optional[int] = None
    professional_name: Optional[str] = None
    datetime: Optional[str] = None
    patient_name: Optional[str] = None
    reason: Optional[str] = None
