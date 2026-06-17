from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, data: UserCreate) -> User | None:
        if self.repository.get_by_email(data.email) is not None:
            return None
        hashed = hash_password(data.password)
        return self.repository.create(data.email, hashed)
