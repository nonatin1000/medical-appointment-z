from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    message: str = Field(min_length=10, description="Clear, friendly message for the user")