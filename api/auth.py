from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from core.database import connect_db, create_user, get_user_by_email
from core.auth_utils import create_access_token, verify_password, get_hash_password
from datetime import timedelta
from datetime import datetime
from models.schemas import UserRegister, LoginRequest
import logging
import traceback


router = APIRouter()


@app.get("/healthz", include_in_schema=False)
def health():
    return {"status": "ok"}


@router.post("/signup")
def signup(user: UserRegister):
    try:
        if get_user_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_hash_password(user.password)
        create_user(user.name, user.email, hashed_password)
        return {"message": "User registered successfully"}
    
    except Exception as e:
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/login")
def login(request: LoginRequest):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT email, password FROM "user" WHERE email = %s', (request.email,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": request.email},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}
