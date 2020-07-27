from sqlalchemy.orm import Session

from projectfiles import models, schema
from pydantic import ValidationError
from datetime import date, datetime
import bcrypt, re

def create_patient(db:Session, patient: schema.PatientCreate):
    hashed_password = bcrypt.hashpw(patient.password.encode("utf-8"), bcrypt.gensalt())
    name = ""
    p = patient.name.split()
    for i in p:
                # print(i)
                i = i.capitalize()
                name = name + " " +i
    patient.name = name
    db_patient = models.Patient(username=patient.username, password=hashed_password, email=patient.email, name =patient.name, birth_date=patient.birth_date)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def select_all_patients(db:Session):
    try:
        return db.query(models.Patient).all()
    except ValidationError as e:
        return (e.json())

def select_by_email(db:Session, email:str):
    return db.query(models.Patient).filter(models.Patient.email==email).first()

def select_by_username(db:Session, username:str):
    return db.query(models.Patient).filter(models.Patient.username==username).first()

def check_username_password(db: Session, user: schema.PatientLogin):
    db_user_info: models.Patient = select_by_username(db, username=user.username)
    print(user.password)
    print(db_user_info.password)
    return bcrypt.checkpw(user.password.encode('utf-8'), db_user_info.password.encode('utf-8'))

def update_patient(new_password: str , new_birt_date: str, db: Session, user: schema.Patient):
    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        user.password = hashed_password
    else:
        hashed_password = user.password
    if new_birt_date:
        user.birth_date = datetime.strptime(new_birt_date, "%Y-%m-%d")
    else:
        new_birt_date = user.birth_date
    db.query(models.Patient).filter(models.Patient.username==user.username).update({"password":hashed_password,"birth_date":new_birt_date})
    return db.commit()