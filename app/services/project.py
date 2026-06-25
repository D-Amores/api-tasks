from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, user_id: int, data: ProjectCreate) -> Project:
        return self.repository.create(user_id, data)

    def get_project(self, user_id: int, project_id: int) -> Project | None:
        project = self.repository.get(project_id)
        if project is None or project.user_id != user_id:
            return None
        return project

    def list_projects(self, user_id: int) -> list[Project]:
        return self.repository.get_all(user_id)

    def update_project(
        self, user_id: int, project_id: int, data: ProjectUpdate
    ) -> Project | None:
        project = self.get_project(user_id, project_id)
        if project is None:
            return None
        return self.repository.update(project, data)

    def delete_project(self, user_id: int, project_id: int) -> bool:
        project = self.get_project(user_id, project_id)
        if project is None:
            return False
        self.repository.delete(project)
        return True
