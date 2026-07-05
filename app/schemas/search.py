from pydantic import BaseModel

from app.schemas.task import TaskRead


class SearchResult(BaseModel):
    task: TaskRead
    distance: float
