from datetime import date

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek

from app.core.config import settings
from app.schemas.ai_task import ExtractedTaskList

SYSTEM_PROMPT = (
    "You extract actionable tasks from free-form text written in Spanish or English. "
    "Today's date is {today}. Resolve relative dates (e.g. 'mañana', 'next Friday') "
    "into actual calendar dates. If no date is mentioned, leave due_date as null. "
    "Do not invent tasks that are not implied by the text."
)


class TaskExtractionService:
    def __init__(self) -> None:
        llm = ChatDeepSeek(
            model=settings.deepseek_model,
            api_key=settings.deepseek_api_key,  # type: ignore
            temperature=0,
            extra_body={"thinking": {"type": "disabled"}},
        )
        self.structured_llm = llm.with_structured_output(ExtractedTaskList)

    def extract(self, text: str) -> ExtractedTaskList:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(today=date.today().isoformat())),
            HumanMessage(content=text),
        ]
        return self.structured_llm.invoke(messages)  # type: ignore
