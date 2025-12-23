from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import graph
import uvicorn

app = FastAPI(title="Inko Blog Manager API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str

@app.get("/")
async def root():
    return {"message": "Inko Blog Manager API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.session_id}}
        
        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config
        )
        
        reply = result["messages"][-1].content
        
        return ChatResponse(reply=reply, session_id=request.session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
