from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from models.user import User


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectID")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Inventory(BaseModel):
    item_id: str = Field(...)
    condition: str = Field(...)
    category: str = Field(...)
    brand: str = Field(...)
    gender: str = Field(...)
    description: str = Field(...)
    price: float = Field(...)
    size: str = Field(...)
    title: str = Field(...)
    color: str = Field(...)
    images: list = Field(...)


class ListingRequest(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    status: str = "PENDING"
    margin: Optional[float]
    marketplace: str = Field(...)
    deleted: bool = False
    credentials: User = Field(...)
    inventory: List[Inventory] = Field(...)
    items: Optional[List[object]]
    createdAt: datetime = datetime.now()
    events: list = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message
    }
