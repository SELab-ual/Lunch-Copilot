
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class RestaurantTypeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class RestaurantTypeOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class RestaurantCreate(BaseModel):
    name: str
    average_price: int = Field(..., ge=0)
    address: str
    phone: str
    email: EmailStr
    description: Optional[str] = None
    type_id: int

class RestaurantOut(BaseModel):
    id: int
    name: str
    average_price: int
    address: str
    phone: str
    email: EmailStr
    description: Optional[str] = None
    type_id: int
    type_name: str

class RestaurantListItem(BaseModel):
    id: int
    name: str
    average_price: int
    type_name: str

class SearchResponse(BaseModel):
    total: int
    items: List[RestaurantListItem]
