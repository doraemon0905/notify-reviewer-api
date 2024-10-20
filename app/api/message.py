from fastapi import APIRouter, Form

router = APIRouter()

@router.post( "/")
def conversation(
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
     return {
            "response_type": "ephemeral",
            "text": ":alert: Please provide a valid URL"
        }
