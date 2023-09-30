from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from pydantic import Field, BaseModel
from typing import Optional
import models


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal(bind=engine)
        yield db
    finally:
        db.close()


@app.get('/')
async def hello():
    return {'test': 'test works'}