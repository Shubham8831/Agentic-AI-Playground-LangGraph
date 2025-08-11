from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import os
load_dotenv()
key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=key)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# for message_chunk, metadata in chatbot.stream(
#     {"messages":[HumanMessage(content = "what is recipi to make pasta")]},  # first we pass the initial state
#     CONFIG = {'configurable': {'thread_id': 'thread-1'}}, # then we pass the config for thread id
#     stream_mode="messages" # modes for streaming
# ):

# # stream will give a generator object
# # print(type(stream))

# #stream object has message chunk and metadata 
#      if message_chunk.content:
#          print(message_chunk.content, end="", flush=True)