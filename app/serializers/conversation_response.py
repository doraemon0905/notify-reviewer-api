from pydantic import BaseModel

class ConversationResponse(BaseModel):
    response_type: str
    text: str
