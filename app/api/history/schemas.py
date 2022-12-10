import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..search.schemas import SearchResponseSchema


class HistoryBase(BaseModel):
    input: str
    result: SearchResponseSchema = None

    class Config:
        orm_mode = True


class CreateHistorySchema(HistoryBase):
    user_id: Optional[uuid.UUID] = None


class GetHistory(HistoryBase):
    id: int
    created_at: datetime

class HistoryIDSchema (BaseModel):
    history_ids: list[uuid.UUID] = None