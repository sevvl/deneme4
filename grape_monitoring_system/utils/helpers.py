import streamlit as st
import time

def show_progress_spinner(text: str, duration: int = 2):
    """
    Displays a Streamlit spinner with a custom message for a given duration.
    """
    with st.spinner(text):
        time.sleep(duration)

def show_success_message(message: str):
    """
    Displays a Streamlit success message.
    """
    st.success(message)

def show_warning_message(message: str):
    """
    Displays a Streamlit warning message.
    """
    st.warning(message)

def show_error_message(message: str):
    """
    Displays a Streamlit error message.
    """
    st.error(message)

