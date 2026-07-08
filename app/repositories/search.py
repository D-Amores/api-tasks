from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, Task, TaskEmbedding


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_tasks(self, user_id: int, query_vector: list[float], limit: int = 5):
        distance = TaskEmbedding.embedding.cosine_distance(query_vector)
        stmt = (
            select(Task, distance.label("distance"))
            .join(TaskEmbedding, TaskEmbedding.task_id == Task.id)
            .join(Project, Project.id == Task.project_id)
            .where(Project.user_id == user_id)
            .order_by(distance)
            .limit(limit)
        )
        return self.db.execute(stmt).all()
