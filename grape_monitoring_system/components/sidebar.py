import streamlit as st

def create_sidebar():
    st.sidebar.title("🍇 Üzüm Takip Sistemi")
    st.sidebar.markdown("--- ")

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Image Analysis", "History", "Settings", "Bilgi Bankası", "Topluluk Forumu"])

    st.sidebar.markdown("--- ")
    st.sidebar.info("Developed with ❤️ for grape growers.")
    return page

