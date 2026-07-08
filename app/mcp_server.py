from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware

from app.api.deps import get_user_from_token
from app.db.session import SessionLocal
from app.repositories.project import ProjectRepository
from app.repositories.search import SearchRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.embedding import EmbeddingService
from app.services.indexing import index_task
from app.services.project import ProjectService
from app.services.search import SearchService
from app.services.task import TaskService

mcp = FastMCP("Task Manager")


class AuthMiddleware(Middleware):
    async def on_call_tool(self, context, call_next):
        headers = get_http_headers(include_all=True)
        header = headers.get("authorization", "")
        if not header.startswith("Bearer "):
            raise ToolError("Missing or invalid Authorization header")
        token = header.removeprefix("Bearer ").strip()

        db = SessionLocal()
        try:
            user = get_user_from_token(token, db)
            if user is None:
                raise ToolError("Invalid or expired token")
            await context.fastmcp_context.set_state("user_id", user.id)
            return await call_next(context)
        finally:
            db.close()


mcp.add_middleware(AuthMiddleware())


async def _services(ctx: Context):
    db = SessionLocal()
    user_id = await ctx.get_state("user_id")
    return (
        db,
        user_id,
        ProjectService(ProjectRepository(db)),
        TaskService(TaskRepository(db), ProjectRepository(db)),
        SearchService(SearchRepository(db), EmbeddingService()),
    )


@mcp.tool()
async def list_projects(ctx: Context) -> str:
    """List all projects belonging to the current user."""
    db, user_id, project_service, _, _ = await _services(ctx)
    try:
        projects = project_service.list_projects(user_id)
        if not projects:
            return "The user has no projects yet."
        return "\n".join(f"- id={p.id}: {p.name}" for p in projects)
    finally:
        db.close()


@mcp.tool()
async def list_tasks(ctx: Context, project_id: int) -> str:
    """List all tasks in a given project."""
    db, user_id, _, task_service, _ = await _services(ctx)
    try:
        tasks = task_service.list_tasks(user_id, project_id)
        if not tasks:
            return "This project has no tasks."
        return "\n".join(
            f"- id={t.id}: {t.title} (completed={t.completed})" for t in tasks
        )
    finally:
        db.close()


@mcp.tool()
async def create_task(ctx: Context, project_id: int, title: str) -> str:
    """Create a new task with the given title inside a project."""
    db, user_id, _, task_service, _ = await _services(ctx)
    try:
        task = task_service.create_task(user_id, project_id, TaskCreate(title=title))
        index_task(task.id)
        return f"Created task id={task.id}: {task.title}"
    finally:
        db.close()


@mcp.tool()
async def complete_task(ctx: Context, project_id: int, task_id: int) -> str:
    """Mark a task as completed."""
    db, user_id, _, task_service, _ = await _services(ctx)
    try:
        task = task_service.update_task(
            user_id, project_id, task_id, TaskUpdate(completed=True)
        )
        return f"Task {task.id} marked as completed."
    finally:
        db.close()


@mcp.tool()
async def search_tasks(ctx: Context, query: str) -> str:
    """Semantically search the user's tasks by meaning, not exact words."""
    db, user_id, _, _, search_service = await _services(ctx)
    try:
        results = search_service.search(user_id, query, limit=5)
        if not results:
            return "No relevant tasks found."
        return "\n".join(
            f"- id={t.id} (project_id={t.project_id}): {t.title}"
            for t, _distance in results
        )
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
