import asyncio
from pathlib import Path
from typing import Any, cast

import aiosqlite
from langchain_core.messages import SystemMessage
from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict

from app.core.config import settings
from app.core.security import create_acces_token

SYSTEM_PROMPT = (
    "You are a helpful task-management assistant. You can list, create, "
    "complete, and semantically search the user's tasks and projects using "
    "your tools. Always use the tools to check real data before answering; "
    "never make up task or project information. Reply in the same language "
    "the user writes in."
)

DB_PATH = Path("agent_memory.db")

_checkpointer: AsyncSqliteSaver | None = None
_checkpointer_lock = asyncio.Lock()

_llm = ChatDeepSeek(
    model=settings.deepseek_model,
    api_key=settings.deepseek_api_key,  # type: ignore
    temperature=0,
    extra_body={"thinking": {"type": "disabled"}},
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


async def _get_checkpointer() -> AsyncSqliteSaver:
    global _checkpointer
    if _checkpointer is None:
        async with _checkpointer_lock:
            if _checkpointer is None:
                conn = await aiosqlite.connect(str(DB_PATH))
                _checkpointer = AsyncSqliteSaver(conn)
    return _checkpointer


def _build_graph(tools, checkpointer: AsyncSqliteSaver):
    llm_with_tools = _llm.bind_tools(tools)

    def call_model(state: AgentState) -> dict:
        messages = state["messages"]
        if not messages or messages[0].type != "system":
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", call_model)
    graph_builder.add_node("tools", ToolNode(tools))
    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges("agent", tools_condition)
    graph_builder.add_edge("tools", "agent")
    return graph_builder.compile(checkpointer=checkpointer)


async def get_agent(user_email: str):
    internal_token = create_acces_token(subject=user_email)

    connections = cast(
        dict[str, Any],
        {
            "tasks": {
                "transport": "http",
                "url": "http://localhost:8001/mcp",
                "headers": {"Authorization": f"Bearer {internal_token}"},
            }
        },
    )
    client = MultiServerMCPClient(connections)
    tools = await client.get_tools()
    checkpointer = await _get_checkpointer()
    return _build_graph(tools, checkpointer)
