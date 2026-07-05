from app.db.session import SessionLocal
from app.models import Task, TaskEmbedding
from app.services.embedding import EmbeddingService


def index_task(task_id: int) -> None:
    db = SessionLocal()
    embedder = EmbeddingService()
    try:
        task = db.get(Task, task_id)
        if task is None:
            return

        existing = (
            db.query(TaskEmbedding).filter(TaskEmbedding.task_id == task_id).first()
        )
        vector = embedder.embed(task.title)

        if existing is not None:
            existing.embedding = vector
        else:
            db.add(TaskEmbedding(task_id=task_id, embedding=vector))

        db.commit()
    finally:
        db.close()
