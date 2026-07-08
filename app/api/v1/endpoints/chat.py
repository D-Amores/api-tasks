from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_graph import get_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    agent = await get_agent(current_user.email)
    config = {"configurable": {"thread_id": f"user-{current_user.id}"}}

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": payload.message}]},
        config=config,  # type: ignore
    )
    last_message = result["messages"][-1]
    return ChatResponse(reply=last_message.content)
