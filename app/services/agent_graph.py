import sqlite3
from pathlib import Path

from langchain_core.messages import SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict

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


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_graph(tools):
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

    return graph_builder.compile(checkpointer=_checkpointer)


def get_agent(db, user_id: int):
    tools = build_agent_tools(db, user_id)
    return build_graph(tools)
