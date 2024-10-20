from fastapi import APIRouter, Depends

router = APIRouter()

@router.get(
    "/{chat_session_uuid}",
    response_model=list[schemas.ChatMessage],
)
def conversation(
    conversation_request: schemas.ConversationRequest,
    db: Session = Depends(deps.get_db),  # noqa: B008
) -> ConversationResponse:
    """Chat conversation."""
    conversations = Conversations(conversation_request.model_dump(), db).answer()
    return ConversationResponse(
        know_answer=conversations.know_answer,
        document_uuids=conversations.document_uuids,
        qa_uuid=conversations.qa_uuid,
        answer=conversations.answer,
        prompts=conversations.prompts,
        conversation_type=conversations.service,
    )
