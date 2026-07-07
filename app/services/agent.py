import sqlite3
from pathlib import Path

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.config import settings
from app.services.agent_tools import build_agent_tools

SYSTEM_PROMPT = (
    "You are a helpful task-management assistant. You can list, create, "
    "complete, and semantically search the user's tasks and projects using "
    "your tools. Always use the tools to check real data before answering; "
    "never make up task or project information. Reply in the same language "
    "the user writes in."
)

DB_PATH = Path("agent_memory.db")

_conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
_checkpointer = SqliteSaver(_conn)

_llm = ChatDeepSeek(
    model=settings.deepseek_model,
    api_key=settings.deepseek_api_key,  # type: ignore
    temperature=0,
    extra_body={"thinking": {"type": "disabled"}},
)


def get_agent(db, user_id: int):
    tools = build_agent_tools(db, user_id)
    return create_agent(
        model=_llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=_checkpointer,
    )
