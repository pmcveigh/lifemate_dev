from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user_by_username,
    require_role,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
        )
    access_token = create_access_token({"sub": user.username})
    return Token(access_token=access_token)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    require_role(current_user, UserRole.global_admin)
    existing = get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(
        username=body.username,
        role=body.role,
        hashed_password=get_password_hash(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
