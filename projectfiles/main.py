from fastapi import Depends, FastAPI, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta, date, datetime
import re, bcrypt


from projectfiles import crud, models, schema, app
from projectfiles.database import SessionLocal, engine

SECRET_KEY = "b35fd6ae766ab1fca250ed004b598ef303eec3db5b473a320f6e6f75dbfe35e0"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    
    if re.search(regex,email):
        return True
    else:
        return False

"""
Login Functions
"""
def verify_password(plainpass, hashedpass):
    # print(bcrypt.hashpw(plainpass.encode("utf-8"), bcrypt.gensalt()))
    return bcrypt.checkpw(plainpass.encode('utf-8'), hashedpass.encode('utf-8'))

def authenticate_user(db:Session, username: str, password: str):
    user = select_by_username(db,username)
    if not user:
        return False
    if not verify_password(password,user.password):
        return False
    return user

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username:
            token_data = schema.TokenData(username=username)
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.select_by_username(db,token_data.username)
    if user:
        return user
    else:
        raise credentials_exception

@app.post("/login", response_model=schema.Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    login_info = schema.PatientLogin(username=username, password=password)
    user_info = crud.select_by_username(db,login_info.username)
    if user_info:
        check_username_password = crud.check_username_password(db, login_info)
        if check_username_password == True:
            access_token_expires = timedelta(minutes=60)
            access_token = create_access_token(data={"sub":user_info.username}, expires_delta=access_token_expires)
        else:
            raise HTTPException(status_code=401, detail="Wrong password")
    else:
        raise HTTPException(status_code=401, detail="Username not found")
    return {"access_token": access_token, "token_type": "bearer"}

"""
Path Functions
"""
@app.post("/register")
def register_patient(username: str, password: str, email: str, name: str, birth_date: Optional[date] = None, db:Session = Depends(get_db)):
    """Valid date format is 'yyyy-mm-ddd' (without the ticks). Example: 1998-07-27 """
    """
    Updates patient password and birthday
    !!! NOTE: date format is 'yyyy-mm-ddd' (without the ticks)
    Example:
    1998-07-27 is valid
    27-07-1998 is NOT valid
    1998-Jul-27 is NOT valid
    1998/07/27 is NOT valid
    """
    if check_email(email):
        db_patients=crud.select_by_email(db, email)
        if db_patients:
            raise HTTPException(status_code=400, detail="Username already registered")
        else:
            if birth_date:
                try:
                    datetime.strptime(new_birt_date, "%Y-%m-%d")
                except:
                    raise HTTPException(status_code=422, detail="Incorrect date format")
                patient = schema.PatientCreate(username=username, password=password,email=email,name=name,birth_date=birth_date)
                return crud.create_patient(db=db,patient=patient)
            else:
                patient = schema.PatientCreate(username=username, password=password,email=email,name=name)
                return crud.create_patient(db=db,patient=patient)
    return {"Error":{"message":"Invalid email"}}

@app.get("/patients/view",response_model=List[schema.Patient])
def view_all(db:Session = Depends(get_db), current_user: schema.PatientLogin = Depends(get_current_user)):
    """ Get information on ALL available patient """
    patients = crud.select_all_patients(db=db)
    return patients

@app.get("/patients/profile",response_model=schema.Patient)
def view_my_profile(db:Session = Depends(get_db), current_user: schema.Patient = Depends(get_current_user)):
    """ Get information on currently active user"""
    return current_user

@app.put("/patients/profile/update",response_model=schema.Patient)
def update_profile(*,new_password:str=None, new_birthdate: str = None, db:Session = Depends(get_db), current_user: schema.Patient = Depends(get_current_user)):
    """Valid date format is 'yyyy-mm-ddd' (without the ticks). Example: 1998-07-27 """
    """
    Updates patient password and birthday
    !!! NOTE: date format is 'yyyy-mm-ddd' (without the ticks)
    Example:
    1998-07-27 is valid
    27-07-1998 is NOT valid
    1998-Jul-27 is NOT valid
    1998/07/27 is NOT valid
    """
    if new_birthdate:
        try:
            datetime.strptime(new_birthdate, "%Y-%m-%d")
        except:
            raise HTTPException(status_code=422, detail="Incorrect date format")
    crud.update_patient(new_password, new_birthdate,db,current_user)
    new_data = crud.select_by_username(db, current_user.username)
    return new_data