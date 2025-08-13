"""
- pip install langgraph-checkpoint-sqlite
- implement database here
- 

"""


from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver #<--
import sqlite3

#pip install langgraph-checkpoint-sqlite
#LangGraph has 3 types of database (InMemorySaver(RAM based), sqliteSaver(good for prototype) and postgre for production apps)
#both sqlite and postgresql is not in langgraph yet

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
# checkpointer = InMemorySaver()


#CHECKPOINTER SETUP
conn = sqlite3.connect(database = "chatbot.db", check_same_thread=False) # it chatbot.db not exist then it will create it  #THIS MAKES A CONNECTION OBJECT
#check_same_thread is true gives error coz we will use multiple threads BUT sqlite works in single thread so we are removing restriction
checkpointer = SqliteSaver(conn=conn) # behind the schene we have to make a sqlite database (made above)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

checkpointer.list(None) # this gives overall checkpoints stored in database or if we tell that we only want thread 1 so it will give all the checkpoints of the particular thread
#None means we need all the checkpoints


#we need thread ids so,

def retrive_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        # print(checkpoint.config['configurable']['thread_id'])
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    # print(list(all_threads)) # this will give all the unique threads in the list 
    return list(all_threads)



#testing sqlit bd

# CONFIG = {"configurable":{"thread_id":"t1"}}

# response = chatbot.invoke (
#     {
#         "messages":[HumanMessage("my name is shubham")]
#     },
#     config=CONFIG
# )
# print(response)