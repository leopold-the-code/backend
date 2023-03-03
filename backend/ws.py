import pydantic

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.auth import load_user
from backend import models
from backend.config import logger

from tortoise.expressions import Q

router = APIRouter()


class ChatMessage(pydantic.BaseModel):
    receiver_id: int
    message: str


# user_id -> connection
online: dict[int, WebSocket] = {}


async def get_match(user1_id, user2_id) -> models.Match:
    match = await models.Match.get(
        Q(initializer_id=user1_id, responder_id=user2_id)
        | Q(initializer_id=user2_id, responder_id=user1_id)
    )
    return match


@router.websocket("/ws/{token}")
async def websocket_endpoint(conn: WebSocket, token: str):
    await conn.accept()
    user = await load_user(token)
    online[user.id] = conn
    logger.info(f"{user.name} is now online")

    try:
        while True:
            data = ChatMessage(**(await conn.receive_json()))
            match = await get_match(user.id, data.receiver_id)
            await models.Message.create(
                match=match,
                author=user,
                message=data.message,
                status=models.Message.Status.UNSEEN.value,
            )

            if receiver_connection := online.get(data.receiver_id):
                try:
                    await receiver_connection.send_json(
                        {"sender_id": user.id, "message": data.message}
                    )
                except WebSocketDisconnect:  # Receiver is no longer online
                    pass

    except WebSocketDisconnect:  # Sender is no longer online
        logger.info(f"{user.name} is now offline")
