from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserRead
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    user = service.register(data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return user
