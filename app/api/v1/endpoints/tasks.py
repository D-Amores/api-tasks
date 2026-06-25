from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task import TaskService

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), ProjectRepository(db))


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    task = service.create_task(current_user.id, project_id, data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    tasks = service.list_tasks(current_user.id, project_id)
    if tasks is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return tasks


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    task = service.update_task(current_user.id, project_id, task_id, data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    project_id: int,
    task_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    deleted = service.delete_task(current_user.id, project_id, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
