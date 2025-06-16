from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from backend.config import settings  # Moved to config.py
from backend.models import TokenData  # , UserInDB (already imported)
from backend.models import Token, User, UserCreate, UserInDB
from backend.services.unified_user_service import user_service
from backend.utils.jwt_helpers import create_access_token, decode_access_token
from backend.utils.security import get_password_hash, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/signup", response_model=User)
async def signup(user_data: UserCreate):
    db_user = await user_service.user_service.get_user_by_username(user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    new_user = await user_service.create_user(user_data)
    if not new_user:
        # This case should ideally not happen if username check is done first,
        # but as a safeguard / if create_user_in_db has other failure modes.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user",
        )
    return User(id=new_user.id, username=new_user.username)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Example of a protected route (to be added to other APIs later)
# @router.get("/users/me", response_model=User)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    user = await user_service.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return User(id=user.id, username=user.username)  # Return Pydantic User model


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
