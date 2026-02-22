"""
Production-Ready Career Advisor Chatbot
Entry point for the Streamlit application
"""

import streamlit as st
from src.ui.chat_interface import render_chat_interface
from src.utils.logger import setup_logger
from src.utils.config import load_config

logger = setup_logger(__name__)


def main():
    config = load_config()
    st.set_page_config(
        page_title=config["app"]["title"],
        page_icon=config["app"]["icon"],
        layout="wide",
        initial_sidebar_state="expanded",
    )
    logger.info("Application started")
    render_chat_interface(config)


if __name__ == "__main__":
    main()
