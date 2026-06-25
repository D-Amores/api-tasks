from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(db))


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_project(current_user.id, data)


@router.get("", response_model=list[ProjectRead])
def list_projects(
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    return service.list_projects(current_user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    project = service.get_project(current_user.id, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    project = service.update_project(current_user.id, project_id, data)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user),
):
    deleted = service.delete_project(current_user.id, project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
