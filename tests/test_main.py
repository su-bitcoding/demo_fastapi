import os
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Use an in-memory SQLite database for testing
if os.path.exists("test.db"):
    os.remove("test.db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # or "sqlite:///:memory:" for in-memory

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database tables
Base.metadata.create_all(bind=engine)

# Dependency override for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_user_success():
    """Test successful user creation"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@exampl1e.com",
            "development": "dev",
            "production": "prod",
            "staging": "stage",
            "address": "123 Test St"
        }
    )

    print("::::::::::::  ",response.json())
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "User created successfully"}

def test_create_user_duplicate_email():
    """Test creating user with duplicate email"""
    # Create first user
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "duplicate@example.com",
            "development": "dev",
            "production": "prod",
            "staging": "stage",
            "address": "123 Test St"
        }
    )
    assert response.status_code == 200
    
    # Try to create second user with same email
    response = client.post(
        "/users",
        json={
            "name": "Another User",
            "email": "duplicate@example.com",
            "development": "dev2",
            "production": "prod2",
            "staging": "stage2",
            "address": "456 Test St"
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

def test_create_user_invalid_email():
    """Test creating user with invalid email format"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "development": "dev",
            "production": "prod",
            "staging": "stage",
            "address": "123 Test St"
        }
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid email format. Please provide a valid email address"}

def test_create_user_missing_fields():
    """Test creating user with missing required fields"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "all fields are required. Please fill in all fields"}

def test_create_user_empty_fields():
    """Test creating user with empty fields"""
    response = client.post(
        "/users",
        json={
            "name": "",
            "email": "testdata@example.com",
            "development": "",
            "production": "",
            "staging": "",
            "address": ""
        }
    )
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "User created successfully"}

def test_create_user_invalid_json():
    """Test creating user with invalid JSON"""
    response = client.post(
        "/users",
        data="{'invalid': 'json'}"
    )
    assert response.status_code == 422
    assert "detail" in response.json()

def test_create_user_with_extra_fields():
    """Test creating user with extra unknown fields"""
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "testcreatewithextra@example.com",
            "development": "dev",
            "production": "prod",
            "staging": "stage",
            "address": "123 Test St",
        }
    )
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "User created successfully"} 

print("All tests passed")