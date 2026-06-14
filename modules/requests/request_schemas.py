from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class Status(str, Enum):
    pending = "Pending"
    approved = "Approved"
    denied = "Denied"


class RequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lrn: str
    name: str
    academic_year: str
    purpose: str


class RequestResponse(BaseModel):
    id: str
    requestor_id: str
    lrn: str
    name: str
    academic_year: str
    purpose: str
    status: Status
    comments: str
    date_requested: datetime

class RequestStatusPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    status: Status