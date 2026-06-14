from enum import Enum

class Role(str, Enum):
  admin = "Admin"
  registrar = "Registrar"
  teacher = "Teacher"
  requestor = "Requestor"