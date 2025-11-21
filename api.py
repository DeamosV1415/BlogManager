# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated
from typing_extensions import TypedDict
import os

# Load environment variables
load_dotenv(override=True)

# Get API keys
api_key = os.getenv("GOOGLE_API_KEY")
search_key = os.getenv("SEARCH_KEY")

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

# Define State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create graph builder
graph_builder = StateGraph(State)

# Define body function
def body(old_state: State) -> State:
    system_message = """You are a helpful blog-writing assistant.

    1️⃣ First, if the user has not provided a topic yet — ask them what topic they want their blog on.
    2️⃣ Once you know the topic, ask how long they want it to be, offering three choices:
        - short = 100 words
        - medium = 200 words
        - long = 400 words
    3️⃣ When both topic and length are clear, generate a well-written blog post with a suitable title and the correct word length.

    Always be conversational and clear. If anything is missing, politely ask the user before writing the blog.
    """

    if isinstance(old_state, dict):
        messages = old_state.get("messages", [])
    else:
        messages = old_state.messages

    messages = [{"role": "system", "content": system_message}] + messages
    response = llm.invoke(messages)
    new_messages = messages + [{"role": "assistant", "content": response.content}]
    return State(messages=new_messages)

# Build graph
graph_builder.add_node("body", body)
graph_builder.add_edge(START, "body")

# Compile with memory
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Create FastAPI app
app = FastAPI()

# Enable CORS (allows your HTML page to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    # Create config with thread_id from session_id
    config = {"configurable": {"thread_id": request.session_id}}
    
    # Invoke graph
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": request.message}]}, 
        config=config
    )
    
    # Extract reply
    bot_reply = result["messages"][-1].content
    
    return ChatResponse(reply=bot_reply)

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "Blog Writer API is running"}

# Run with: uvicorn api:app --reload