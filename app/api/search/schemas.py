from pydantic import BaseModel, BaseConfig
from typing import Optional, List
from datetime import datetime


class SearchResponseSchema(BaseModel):
    name: str
    gender: Optional[str] = None
    occupation: Optional[List] = []
    age: Optional[int] = None
    is_vip: Optional[bool] = None
    vip_score: Optional[int] = None
    created_at: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SearchParamsSchema(BaseModel):
    name: str
    gender: str = None
    occupation: str = None
    age: int = None
    email: str = None


class SearchListSchema(BaseModel):
    data: List[SearchParamsSchema]
