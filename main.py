import os
import uuid
import shutil
from fastapi import FastAPI, Depends, Request, HTTPException,UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, Field
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Upload, User
from database import SessionLocal, engine, Base
from datetime import datetime

templates = Jinja2Templates(directory="templates")

app = FastAPI()


# Create DB tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for error in errors:
        if error["type"] == "value_error" and "email" in error["loc"]:
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Invalid email format. Please provide a valid email address"
                }
            )
        if error["type"] == "missing":
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "all fields are required. Please fill in all fields"
                }
            )
    return JSONResponse(
        status_code=422,
        content={"detail": [error for error in errors]}
    )

@app.get("/")
def get_template(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


class UserCreate(BaseModel):
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    development: str = Field(..., description="Development environment details")
    production: str = Field(..., description="Production environment details")
    staging: str = Field(..., description="Staging environment details")
    name1: str = Field(..., description="User's name1")
    address: str = Field(..., description="User's address")
    

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email and User.address == user.address).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        development=user.development,
        production=user.production,
        staging=user.staging,
        name1=user.name1,
        address=user.address
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "message": "User created successfully"}

UPLOAD_DIR = "uploads"
IMAGE_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

@app.post("/upload/")
def upload_file(
    username: str = Form(...),
    message: str = Form(None),
    file: UploadFile = File(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    file_path = None
    file_name = None
    file_size = None
    content_type = None

    if file:
        file_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except OSError as e:
            raise HTTPException(status_code=400, detail="Filename too long.")

        file_size = os.path.getsize(file_path)
        content_type = file.content_type

    image_path = None
    image_name = None
    image_size = None

    if image:
        image_name = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join(IMAGE_DIR, image_name)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_size = os.path.getsize(image_path)

    try:
        upload = Upload(
            username=username,
            message=message,
            file_path=file_path,
            image_path=image_path,
            file_name=file.filename if file else None,
            image_name=image.filename if image else None,
            file_size=file_size,
            image_size=image_size,
            content_type=content_type,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        return {"message": "Upload successful", "id": upload.id}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
