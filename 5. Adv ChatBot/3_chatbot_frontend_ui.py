import streamlit as st
from chatbot_backend_2 import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {'configurable': {'thread_id': 'thread-1'}}


# st.session_state -> dict ->  special type of dictionary that does not erase its content when we press enter it only erases when we refresh page manually
#if not then add a enpty list
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']): #loading role
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hi=ello'}

user_input = st.chat_input('Type here...')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    
    # ai_message = response['messages'][-1].content 
    # # first add the message to message_history
    # st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    # with st.chat_message('assistant'):
    #     st.text(ai_message)


    # THE ABOVE INVOKE WAY TO PROVIDE USER MESSAGES IS BAD AS IT FIRST GENERATES THE RESPONSE AND THEN IT PRINTS ALL AT ONCE

    # STREAMING - to get token by token output form the llm (the models start sending tokens (messages) 
    # as soon as they are generated instead of wating for entire response to be reaby before returning it)

    #so rather then using .invoke we use .stream -> this returns a generator object -> 
    # -> generator object is a special type of iterator that allows you to generate values one at a time, using yield keyword instead of return


  #  st.write_stream : write generator or streams to the app with a typewriter effect
   
    # STREAMING IMPLEMENTATION : 
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= {'configurable': {'thread_id': 'thread-1'}},
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message}) # SAVING THE OUTPUT OF ASSISTANT