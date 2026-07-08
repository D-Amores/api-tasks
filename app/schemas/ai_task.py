from datetime import date

from pydantic import BaseModel, Field


class ExtractedTask(BaseModel):
    title: str = Field(description="Short, clear title for the task")
    due_date: date | None = Field(
        default=None, description="Due date if mentioned or inferable, else null"
    )


class ExtractedTaskList(BaseModel):
    tasks: list[ExtractedTask] = Field(description="All tasks found in the text")


class ExtractRequest(BaseModel):
    text: str
