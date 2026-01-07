from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Login with username or email"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str
    
    @model_validator(mode='after')
    def check_username_or_email(self):
        """Ensure at least one of username or email is provided"""
        if not self.username and not self.email:
            raise ValueError("Either username or email must be provided")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "yourpassword"
            }
        }


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

