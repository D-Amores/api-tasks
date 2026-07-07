from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_graph import get_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = get_agent(db, current_user.id)
    config = {"configurable": {"thread_id": f"user-{current_user.id}"}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": payload.message}]},
        config=config,  # type: ignore
    )
    last_message = result["messages"][-1]
    return ChatResponse(reply=last_message.content)
