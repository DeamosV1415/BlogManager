from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def body(old_state: State) -> State:
    system_message = """You are Inko, a highly skilled professional blog-writing assistant.

    Your goal is to help the user create high-quality, engaging, and well-structured blog posts. Follow this structured discovery process:

    1️⃣ **Topic & Purpose**: First, ask the user what topic they want to write about and what the primary goal of the blog is (e.g., to inform, persuade, or entertain).
    2️⃣ **Audience & Tone**: Once you have the topic, ask who the target audience is and what tone they would like:
        - Professional (Serious, authoritative, and formal)
        - Conversational (Friendly, relatable, and easy to read)
        - Persuasive (Convincing, benefit-driven, and energetic)
        - Technical (Detailed, factual, and jargon-appropriate)
    3️⃣ **Length Selection**: Finally, ask for the desired length, offering these options:
        - Short (300 - 400 words): Perfect for quick tips or news updates.
        - Medium (700 - 800 words): Great for detailed guides and listicles.
        - Long (1200+ words): Ideal for in-depth analysis and comprehensive deep dives.

    When all information is clear, generate a well-written blog post with a compelling title. 

    **CRITICAL RULES**:
    - Always be conversational, polite, and professional.
    - If any information is missing, ask the user clearly before proceeding.
    - IMPORTANT: Do not use any markdown formatting like asterisks (*), hashtags (#), or other special characters. Write in plain text only. Ensure the output is clean and ready for direct use.
    """

    if isinstance(old_state, dict):
        messages = old_state.get("messages", [])
    else:
        messages = old_state.messages

    messages = [{"role": "system", "content": system_message}] + messages
    response = llm.invoke(messages)
    
    # Clean up any remaining markdown
    clean_content = response.content.replace("**", "").replace("*", "").replace("###", "").replace("##", "").replace("#", "")
    
    new_messages = messages + [{"role": "assistant", "content": clean_content}]
    return State(messages=new_messages)

graph_builder.add_node("body", body)
graph_builder.add_edge(START, "body")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)