from app.core.exceptions import ConflictError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, data: UserCreate) -> User | None:
        if self.repository.get_by_email(data.email) is not None:
            raise ConflictError("Email already registered")
        hashed = hash_password(data.password)
        return self.repository.create(data.email, hashed)

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.repository.get_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
