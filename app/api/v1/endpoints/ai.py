from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.schemas.ai_task import ExtractRequest
from app.schemas.task import TaskCreate, TaskRead
from app.services.indexing import index_task
from app.services.task import TaskService
from app.services.task_extraction import TaskExtractionService

router = APIRouter(prefix="/ai", tags=["ai"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db), ProjectRepository(db))


@router.post("/projects/{project_id}/extract-tasks", response_model=list[TaskRead])
def extract_tasks(
    project_id: int,
    payload: ExtractRequest,
    background_tasks: BackgroundTasks,
    service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user),
):
    extraction = TaskExtractionService()
    extracted = extraction.extract(payload.text)

    created_tasks = []
    for item in extracted.tasks:
        data = TaskCreate(title=item.title)
        task = service.create_task(current_user.id, project_id, data)
        background_tasks.add_task(index_task, task.id)
        created_tasks.append(task)

    return created_tasks
