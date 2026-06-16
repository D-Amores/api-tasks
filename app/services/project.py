from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, data: ProjectCreate) -> Project:
        return self.repository.create(data)

    def get_project(self, project_id: int) -> Project | None:
        return self.repository.get(project_id)

    def list_projects(self) -> list[Project]:
        return self.repository.get_all()

    def update_project(self, project_id: int, data: ProjectUpdate) -> Project | None:
        project = self.repository.get(project_id)
        if project is None:
            return None
        return self.repository.update(project, data)

    def delete_project(self, project_id: int) -> bool:
        project = self.repository.get(project_id)
        if project is None:
            return False
        self.repository.delete(project)
        return True
