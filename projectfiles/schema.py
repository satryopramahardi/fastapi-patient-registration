from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class PatientBase(BaseModel):
    username: str

class PatientLogin(PatientBase):
    password: str

class PatientDisplay(PatientBase):
    email: str
    name: str
    birth_date: date = None

class PatientCreate(PatientBase):
    password: str
    email: str
    name: str
    birth_date: date = None

class Patient(PatientBase):
    id = int
    password: str
    email: str
    name: str
    birth_date: date = None
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None