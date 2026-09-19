from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google ID Token from Google Sign-In button or One Tap")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token previously issued")
