from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.repositories.project import ProjectRepository
from app.repositories.search import SearchRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.embedding import EmbeddingService
from app.services.indexing import index_task
from app.services.project import ProjectService
from app.services.search import SearchService
from app.services.task import TaskService


def build_agent_tools(db: Session, user_id: int):
    """Builds the toolset for one user. Closures bind user_id so the LLM
    never chooses whose data it touches."""

    project_service = ProjectService(ProjectRepository(db))
    task_service = TaskService(TaskRepository(db), ProjectRepository(db))
    search_service = SearchService(SearchRepository(db), EmbeddingService())

    @tool
    def list_projects() -> str:
        """List all projects belonging to the current user."""
        projects = project_service.list_projects(user_id)
        if not projects:
            return "The user has no projects yet."
        return "\n".join(f"- id={p.id}: {p.name}" for p in projects)

    @tool
    def list_tasks(project_id: int) -> str:
        """List all tasks in a given project."""
        tasks = task_service.list_tasks(user_id, project_id)
        if not tasks:
            return "This project has no tasks."
        return "\n".join(
            f"- id={t.id}: {t.title} (completed={t.completed})" for t in tasks
        )

    @tool
    def create_task(project_id: int, title: str) -> str:
        """Create a new task with the given title inside a project."""
        task = task_service.create_task(user_id, project_id, TaskCreate(title=title))
        index_task(task.id)
        return f"Created task id={task.id}: {task.title}"

    @tool
    def complete_task(project_id: int, task_id: int) -> str:
        """Mark a task as completed."""
        task = task_service.update_task(
            user_id, project_id, task_id, TaskUpdate(completed=True)
        )
        return f"Task {task.id} marked as completed."

    @tool
    def search_tasks(query: str) -> str:
        """Semantically search the user's tasks by meaning, not exact words."""
        results = search_service.search(user_id, query, limit=5)
        if not results:
            return "No relevant tasks found."
        return "\n".join(
            f"- id={t.id} (project_id={t.project_id}): {t.title}"
            for t, _distance in results
        )

    return [list_projects, list_tasks, create_task, complete_task, search_tasks]
