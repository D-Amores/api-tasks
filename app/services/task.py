from app.core.exceptions import NotFoundError
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

    def _owned_project(self, user_id: int, project_id: int):
        project = self.project_repository.get(project_id)

        if project is None or project.user_id != user_id:
            raise NotFoundError("Project not found")
        return project

    def create_task(
        self, user_id: int, project_id: int, data: TaskCreate
    ) -> Task | None:
        self._owned_project(user_id, project_id)
        return self.task_repository.create(project_id, data)

    def list_tasks(self, user_id: int, project_id: int) -> list[Task] | None:
        self._owned_project(user_id, project_id)
        return self.task_repository.get_by_project(project_id)

    def get_task(self, user_id: int, project_id: int, task_id: int) -> Task:
        self._owned_project(user_id, project_id)
        task = self.task_repository.get(task_id)

        if task is None or task.project_id != project_id:
            raise NotFoundError("Task not found")
        return task

    def update_task(
        self, user_id: int, project_id: int, task_id: int, data: TaskUpdate
    ) -> Task | None:
        task = self.get_task(user_id, project_id, task_id)
        return self.task_repository.update(task, data)

    def delete_task(self, user_id: int, project_id: int, task_id: int) -> bool:
        task = self.get_task(user_id, project_id, task_id)
        self.task_repository.delete(task)
        return True
