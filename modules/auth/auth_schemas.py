from pydantic import BaseModel, EmailStr, ConfigDict


class AuthRequestorOtpDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr

class AuthVerifyOtpDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr
  otp: str

class AuthLoginDTO(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr
  password: str