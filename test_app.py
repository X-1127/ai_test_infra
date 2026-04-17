from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "LLM Mock Server is running"}

@app.post("/chat")
def chat(message: Message):
    return {"response": f"Mock response to: {message.message}"}