from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_id: int, data: TaskCreate) -> Task:
        task = Task(**data.model_dump(), project_id=project_id)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_project(self, project_id: int) -> list[Task]:
        stmt = select(Task).where(Task.project_id == project_id)
        return list(self.db.scalars(stmt).all())

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def update(self, task: Task, data: TaskUpdate) -> Task:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
