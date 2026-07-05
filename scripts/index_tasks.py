from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Task, TaskEmbedding
from app.services.embedding import EmbeddingService


def main():
    db = SessionLocal()
    embedder = EmbeddingService()
    try:
        already_indexed = set(db.scalars(select(TaskEmbedding.task_id)).all())
        tasks = db.scalars(select(Task)).all()

        new_count = 0
        for task in tasks:
            if task.id in already_indexed:
                continue
            vector = embedder.embed(task.title)
            db.add(TaskEmbedding(task_id=task.id, embedding=vector))
            print(f"Indexed task {task.id}: {task.title}")
            new_count += 1

        db.commit()
        print(f"\nDone. {new_count} new task(s) indexed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
