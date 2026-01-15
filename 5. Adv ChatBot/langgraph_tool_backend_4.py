"""
TOOL NODE - prebuild node type that acts as a bridge between your graph adn external tools 
it is ready made tool that knows how to handle a list of tools
its job - is to listen for tool call sfrom the llm and automatically route the request to the correct tool, then pass the tool output back into the graph
"""

"""
TOOL_CONDITIONS - prebuild conditional edge fn that helps your graph decide; should the flow go to the toolnode next or back to llm?
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



from langgraph.prebuilt import ToolNode, tools_condition 
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool # to make custom tool
import requests

from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
import os
load_dotenv()
key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=key)



#Tools
search_tool = DuckDuckGoSearchRun(region = "us-en")

@tool
def calculator(first_num: float, second_num: float, operation:str) -> dict:
    """
    Perform a basic arithmentic operaion on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation =="add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num":second_num, "operation":operation, "result":result}
    
    except Exception as ex:
        return {"error": str(ex)}
    




@tool
def get_stock_price(symbol:str)->dict:
    """
    Fetch latest stock price for a given symbol (e.g. "AAPL", "TSLA")
    using Alpha Vantage with API key in the URL
    """

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=WAWAA1HR20EIM0XX"
    r = requests.get(url)
    return r.json()
    

#make tool list 
tools = [search_tool, get_stock_price, calculator]

#make the LLM tool aware

llm_with_tool = llm.bind_tools(tools)




# STATE
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


#NODE
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm_with_tool.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools) # maKIGN TOOL NODE

# Checkpointer
# checkpointer = InMemorySaver()


#CHECKPOINTER SETUP
conn = sqlite3.connect(database = "chatbot.db", check_same_thread=False) # it chatbot.db not exist then it will create it  #THIS MAKES A CONNECTION OBJECT
#check_same_thread is true gives error coz we will use multiple threads BUT sqlite works in single thread so we are removing restriction
checkpointer = SqliteSaver(conn=conn) # behind the schene we have to make a sqlite database (made above)



graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node", tools_condition)

graph.add_edge("tools", "chat_node")



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


