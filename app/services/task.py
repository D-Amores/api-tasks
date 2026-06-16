from app.models.task import Task
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(
        self, task_repository: TaskRepository, project_repository: ProjectRepository
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository

    def create_task(self, project_id: int, data: TaskCreate) -> Task | None:
        if self.project_repository.get(project_id) is None:
            return None

        return self.task_repository.create(project_id, data)

    def list_tasks(self, project_id: int) -> list[Task] | None:
        if self.project_repository.get(project_id) is None:
            return None

        return self.task_repository.get_by_project(project_id)

    def get_task(self, project_id: int, task_id: int) -> Task | None:
        task = self.task_repository.get(task_id)
        if task is None or task.project_id != project_id:
            return None
        return task

    def update_task(
        self, project_id: int, task_id: int, data: TaskUpdate
    ) -> Task | None:
        task = self.get_task(project_id, task_id)
        if task is None:
            return None
        return self.task_repository.update(task, data)

    def delete_task(self, project_id: int, task_id: int) -> bool:
        task = self.get_task(project_id, task_id)
        if task is None:
            return False
        self.task_repository.delete(task)
        return True
