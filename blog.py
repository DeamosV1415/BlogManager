# %%
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
from langgraph.prebuilt import ToolNode, tools_condition
import requests
import os
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated
from typing_extensions import TypedDict
import gradio as gr

# %%
load_dotenv(override=True)

# %%
api_key=os.getenv("GOOGLE_API_KEY")
search_key=os.getenv("SEARCH_KEY")
if(api_key and search_key):
    print("Well and done")

# %%
#loading Model
llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

# %%
class State(TypedDict):
    messages:Annotated[list,add_messages]

graph_builder=StateGraph(State)

# %%
# #agent 1
# def chat(old_state: State) -> State:
#     system_message = f"""Your role is to talk to the user about the topic on which the blog
#     needs to be generated. You must provide a blog title and ask the user
#     to choose a blog length. Offer three choices:
#     call {writer} blog when user provide length.
#     1. short = 100 words
#     2. medium = 200 words
#     3. long = 400 words.
#     """
#     messages = old_state.get("messages", []) if isinstance(old_state, dict) else old_state.messages
#     messages = [{"role": "system", "content": system_message}] + messages

#     title = llm.invoke(messages)
#     new_messages = messages + [{"role": "assistant", "content": title.content}]
#     return State(messages=new_messages)


# %%
def body(old_state: State) -> State:
    system_message = """You are a helpful blog-writing assistant.

    1️ First, if the user has not provided a topic yet — ask them what topic they want their blog on.
    2️ Once you know the topic, ask how long they want it to be, offering three choices:
        - short = 100 words
        - medium = 200 words
        - long = 400 words
    3️ When both topic and length are clear, generate a well-written blog post with a suitable title and the correct word length.

    Always be conversational and clear. If anything is missing, politely ask the user before writing the blog.
    """

    # --- Handle message accumulation safely ---
    if isinstance(old_state, dict):
        messages = old_state.get("messages", [])
    else:
        messages = old_state.messages

    # Prepend the system instruction
    messages = [{"role": "system", "content": system_message}] + messages

    # --- Invoke LLM ---
    response = llm.invoke(messages)

    # --- Return updated state ---
    new_messages = messages + [{"role": "assistant", "content": response.content}]
    return State(messages=new_messages)


# %%
#graph builder nodes
graph_builder.add_node("body",body)


# %%
#edges
graph_builder.add_edge(START,"body")


memory=MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
display(Image(graph.get_graph().draw_mermaid_png()))

# %%
config = {"configurable": {"thread_id": "10"}}
async def chat(user_input: str, history):
    result = await graph.ainvoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return result["messages"][-1].content


gr.ChatInterface(chat, type="messages").launch()

# %%



