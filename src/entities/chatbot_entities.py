from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MediaPayload(BaseModel):
    url: Optional[str] = None
    mimetype: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None

class MessagePayload(BaseModel):
    id: str
    timestamp: int
    from_: str = Field(alias="from")
    fromMe: bool
    body: str
    hasMedia: bool
    ack: Optional[int] = None
    _data: Optional[Dict[str, Any]] = None
    media: Optional[MediaPayload] = None

class WahaRequest(BaseModel):
    event: str
    session: str
    payload: MessagePayload
