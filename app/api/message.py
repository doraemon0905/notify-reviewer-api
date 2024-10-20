from fastapi import APIRouter, Form
from app.serivces.send_message import SendMessage

router = APIRouter()

@router.post("/")
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
    trigger_id: str = Form(...)
):
    try:
        message_service = SendMessage(user_id, text)
        await message_service.send()
        return {
            "response_type": "ephemeral",
            "text": ":white_check_mark: Your request has been submitted successfully."
        }
    except Exception as e:
        return {
            "response_type": "ephemeral",
            "text": ":alert: " + str(e)
        }
