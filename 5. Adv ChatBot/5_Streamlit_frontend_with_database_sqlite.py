# WE HAVE TO ONLY CHANGE SESSION SETUP

import streamlit as st
from chatbot_database_backend_3 import chatbot, retrive_all_threads
from langchain_core.messages import HumanMessage
import uuid #  generate unique thread identifiers.

# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id # returns uuid object not string

def reset_chat():
    thread_id = generate_thread_id()   #Generates a new thread id.
    st.session_state['thread_id'] = thread_id  #Stores it in st.session_state['thread_id'] (Streamlit’s per-session storage).
    add_thread(st.session_state['thread_id'])   # Calls add_thread(...) to add the new thread id into the list of saved chats.
    st.session_state['message_history'] = [] # Resets the in-memory message_history to an empty list so the UI shows a fresh chat.

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id) #If the given thread_id is not already in the chat_threads list in session state, append it. Ensures no duplicate thread IDs in the list.

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages'] # ask the backend chatbot for the saved messages for this thread id


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    # st.session_state['chat_threads'] = [] #so when session reloads then we are always setting new chat_thread BUT now we have a sqlite database which will have all the threads
    # now we will have to pass the thread_ids in the []
    st.session_state['chat_threads'] = retrive_all_threads()

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat', type='primary', use_container_width=True):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:   #Iterates over chat_threads in reverse order 

    # Safely try to load messages; default to []
    state_values = chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values
    messages = state_values.get('messages', [])

    # Find the last HumanMessage in this thread
    last_user_msg = next(
        (msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)),
        "chats"
    )

    # Use first ~30 chars for the button label
    label = last_user_msg[:20] + ("..." if len(last_user_msg) > 30 else "")

    if st.sidebar.button(label, key=f"btn_{thread_id}", type="secondary"):   # Creates a sidebar button labelled with str(thread_id).
        st.session_state['thread_id'] = thread_id   # Sets the session's thread_id to this thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


# **************************************** Main UI ************************************

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})