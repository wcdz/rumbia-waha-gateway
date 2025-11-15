from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MediaPayload(BaseModel):
    url: Optional[str] = None
    mimetype: Optional[str] = None
    filename: Optional[str] = None

class MessagePayload(BaseModel):
    id: str
    timestamp: int
    from_: str = Field(alias="from")
    fromMe: bool
    body: Optional[str] = None
    hasMedia: bool
    media: Optional[MediaPayload] = None

class WahaRequest(BaseModel):
    event: str
    session: str
    payload: MessagePayload
