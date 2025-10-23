from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class EventSchema(BaseModel):
    topic: str = Field(..., description="Nama topik event")
    event_id: str = Field(..., description="ID unik event")
    timestamp: datetime = Field(..., description="Waktu event (ISO 8601)")
    source: str | None = None
    payload: Any | None = None