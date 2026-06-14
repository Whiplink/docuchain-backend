from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from core.enums import Role

class AccountsRequestDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr
  password: str
  role: Role

class AccountsResponseDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  id: str
  email: EmailStr
  role: Role

class AccountsCreateDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr
  password: str
  role: Role
  otp: str
  otp_expires_at: datetime

class AccountsRoleDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  role: Role
