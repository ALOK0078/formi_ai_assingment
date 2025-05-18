from fastapi import FastAPI, Request
from app.state_machine import ConversationManager
from app.google_sheet import log_to_sheet

app = FastAPI()
chatbot = ConversationManager()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")
    state, response = chatbot.handle_input(user_input)
    return {"state": state, "response": response}

@app.post("/log_conversation")
async def log_conversation(request: Request):
    data = await request.json()
    log_to_sheet(data)
    return {"status": "logged"}