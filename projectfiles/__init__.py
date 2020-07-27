from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")
app = FastAPI()

app.mount("/static", StaticFiles(directory="./projectfiles/static"), name='static')
templates = Jinja2Templates(directory="./projectfiles/templates")

from projectfiles import main
