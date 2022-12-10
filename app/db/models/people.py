from typing import Optional, List
from db.models.common import TimestampModel, UUIDModel
from sqlmodel import Field, Column, JSON

class People(TimestampModel, UUIDModel, table=True):
    __tablename__ = "people"

    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[List[str]] = Field(sa_column=Column(JSON))
    vip_score: int
    is_vip: bool

    # Needed for Column(JSON)
    class Config:
        arbitrary_types_allowed = True
        
    def __repr__(self):
        return f"<Person (id: {self.id})>"
