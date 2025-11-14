from components.chat_interface import ChatInterface
from components.sidebar import create_sidebar

import streamlit as st

st.set_page_config(
    page_title="MartAI",
    page_icon="🤖",
    layout="wide",
)

create_sidebar()

st.title("DevMentor AI")

chat = ChatInterface()

chat.display_messages()

chat.handle_user_input()

chat.display_chat_stats()
