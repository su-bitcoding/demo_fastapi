from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, Field
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal, engine, Base

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
        address=user.address
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "message": "User created successfully"}


