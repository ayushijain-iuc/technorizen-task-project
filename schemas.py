from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)  # Bcrypt 72-byte limit


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Profile Schemas
class ProfileCreate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=150)
    phone_no: Optional[str] = Field(None, max_length=20)
    profile_photo: Optional[str] = None


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=150)
    phone_no: Optional[str] = Field(None, max_length=20)
    profile_photo: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    phone_no: Optional[str]
    profile_photo: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Server Schemas
class ServerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    host: str = Field(..., min_length=1)
    port: int = Field(22, ge=1, le=65535)
    username: str = Field(..., min_length=1)
    password: Optional[str] = None
    ssh_key: Optional[str] = None
    description: Optional[str] = None


class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    host: Optional[str] = Field(None, min_length=1)
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = None
    ssh_key: Optional[str] = None
    description: Optional[str] = None


class ServerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    host: str
    port: int
    username: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Command Execution Schemas
class CommandExecute(BaseModel):
    server_id: int
    command: str = Field(..., min_length=1)


class CommandResponse(BaseModel):
    success: bool
    output: Optional[str]
    error: Optional[str]
    exit_status: Optional[int]
    execution_time: datetime


class CommandLogResponse(BaseModel):
    id: int
    user_id: int
    server_id: int
    command: str
    output: Optional[str]
    error: Optional[str]
    exit_status: Optional[int]
    execution_time: datetime
    
    class Config:
        from_attributes = True

