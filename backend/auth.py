
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from db import find_user_by_username

# --- Configuration ---
# In a real production app, this should be loaded from a secure environment variable
SECRET_KEY = "b2a3f8e1c9d0a4f5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9" # Replace with your own key

# --- THIS IS THE FIX ---
# The correct algorithm is HS256, not HS2256
ALGORITHM = "HS256" 
# --- END OF FIX ---

ACCESS_TOKEN_EXPIRE_MINUTES = 480

# This tells FastAPI that the URL to get a token is "/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- Helper Functions ---
def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verifies a plain password against a hashed one."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    except Exception:
        return False

def create_access_token(data: dict):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- The "Get Current User" Dependency ---
def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Decodes the JWT token from the request header, verifies it,
    and returns the user's username.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = find_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user.get("username")