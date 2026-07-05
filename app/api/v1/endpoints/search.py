from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.repositories.search import SearchRepository
from app.schemas.search import SearchResult
from app.schemas.task import TaskRead
from app.services.embedding import EmbeddingService
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    return SearchService(SearchRepository(db), EmbeddingService())


@router.get("/tasks", response_model=list[SearchResult])
def search_tasks(
    q: str,
    service: SearchService = Depends(get_search_service),
    current_user: User = Depends(get_current_user),
):
    results = service.search(current_user.id, q)
    return [
        SearchResult(task=TaskRead.model_validate(task), distance=distance)
        for task, distance in results
    ]
