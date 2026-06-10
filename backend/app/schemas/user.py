from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ProfileBase(BaseModel):
    ftp: int
    w_prime: int
    resting_hr: int
    max_hr: int
    weight_kg: float
    power_zones: Optional[Dict[str, Any]] = None
    hr_zones: Optional[Dict[str, Any]] = None
    weekly_availability: Optional[Dict[str, Any]] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    user_id: UUID

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True
