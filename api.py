import json
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
import uvicorn
from llm import handle_prompt, SYSTEM_PROMPT, handle_prompt_with_image
import uuid

app = FastAPI(
    title="Shopping Assistant API",
    description="API for the Meeting Assistant chatbot",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_sessions: Dict[str, List[Dict[str, Any]]] = {}

class ChatRequest(BaseModel):
    message: Optional[str] = None
    raw_image: Optional[str] = None
    session_id: Optional[str] = None

    @validator('raw_image')
    def validate_raw_image(cls, v):
        if v is not None:
            try:
                base64.b64decode(v)
            except Exception as e:
                raise ValueError(f"Invalid base64 image data: {str(e)}")
        return v

class Product(BaseModel):
    name: str
    description: str
    brand: str
    category: str
    price: int

class ChatResponse(BaseModel):
    session_id: str
    response: str


def load_image_into_response(json_res) -> str:
    json_res_content = json.loads(json_res['content'])
    image_encoded = encode_image_to_base64(json_res_content['image_url'])
    json_res_content['image_encoded'] = image_encoded
    json_res['content'] = json_res_content
    return json.dumps(json_res)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for interacting with the Shopping Assistant chatbot.
    
    This endpoint supports both text messages and image uploads, and maintains chat sessions
    for continuous conversations.
    
    Parameters:
    - message (optional): Text message to send to the assistant
    - raw_image (optional): Base64 encoded image data
    - session_id (optional): UUID of an existing chat session. If not provided, a new session will be created
    
    Note: At least one of message or raw_image must be provided.
    
    Returns:
    - session_id: UUID of the chat session (new or existing)
    - response: Assistant's response in JSON format
    """
    try:
        if not request.message and not request.raw_image:
            raise HTTPException(
                status_code=422,
                detail="Either message or raw_image must be provided"
            )

        if request.session_id:
            if request.session_id not in chat_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            chat_history = chat_sessions[request.session_id]
        else:
            session_id = str(uuid.uuid4())
            chat_history = [
                {"role": "system", "content": SYSTEM_PROMPT},
            ]
            chat_sessions[session_id] = chat_history

        if request.raw_image:
            message = request.message or 'find something like this image'
            response = handle_prompt_with_image(message, request.raw_image, chat_history)
        else:
            response = handle_prompt(request.message, chat_history)

        json_res = json.loads(response)
        if json_res['type'] == 'json':
            response = load_image_into_response(json_res)

        return ChatResponse(
            session_id=request.session_id or session_id,
            response=response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)