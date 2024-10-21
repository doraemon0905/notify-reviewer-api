from fastapi import APIRouter, Form
from app.serivces.send_message import SendMessage
from app.serializers.conversation_response import ConversationResponse
from fastapi.responses import JSONResponse
from app.utils.sentry import capture_exception

router = APIRouter()


@router.post("/", response_model=ConversationResponse)
async def conversation(
    token: str = Form(...),
    team_id: str = Form(...),
    team_domain: str = Form(...),
    channel_id: str = Form(...),
    channel_name: str = Form(...),
    user_id: str = Form(...),
    user_name: str = Form(...),
    command: str = Form(...),
    text: str = Form(...),
    response_url: str = Form(...),
    trigger_id: str = Form(...),
):
    try:
        message_service = SendMessage(user_id, text)
        await message_service.send()
        return ConversationResponse(
            response_type="ephemeral",
            text=":white_check_mark: Your request has been submitted successfully.",
        )
    except Exception as e:
        capture_exception(e)
        return JSONResponse(
            status_code=400,
            content=ConversationResponse(
                response_type="ephemeral", text=":alert: " + str(e)
            ).model_dump(),
        )
