"""
Chat Interface Module - Fixed Version
- Shows real API error messages with diagnosis tips
- Added API key debug panel in sidebar
- Fixed avatar issue (no emoji avatars)
"""

import os
import streamlit as st
from src.api.gemini_handler import get_model, send_message, validate_api_connection
from src.utils.session import (
    create_session, add_message, get_history_for_api,
    get_message_count, clear_session
)
from src.prompts.career_prompts import get_welcome_message
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def _init_session_state(config: dict) -> None:
    """Initialize all Streamlit session state variables."""
    if "session" not in st.session_state:
        st.session_state.session = create_session()
        logger.info(f"New session started: {st.session_state.session.session_id}")

    if "model" not in st.session_state:
        try:
            st.session_state.model = get_model()
            st.session_state.api_ready = True
            st.session_state.api_error = None
        except EnvironmentError as e:
            st.session_state.api_ready = False
            st.session_state.api_error = str(e)
            st.session_state.model = None
        except Exception as e:
            st.session_state.api_ready = False
            st.session_state.api_error = f"[{type(e).__name__}] {str(e)}"
            st.session_state.model = None

    if "messages_display" not in st.session_state:
        st.session_state.messages_display = [
            {"role": "assistant", "content": get_welcome_message()}
        ]


def _get_error_hint(error_str: str) -> str:
    """Return a human-friendly fix based on the error type."""
    e = error_str.lower()
    if "api_key" in e or "api key" in e or "invalid" in e and "key" in e:
        return "🔑 **Fix:** Your `GEMINI_API_KEY` is invalid. Get a valid key at https://aistudio.google.com/apikey and update your `.env` file."
    if "permission" in e or "403" in e:
        return "🔒 **Fix:** API key doesn't have permission. Make sure the Gemini API is enabled in your Google Cloud project."
    if "quota" in e or "exhausted" in e or "429" in e:
        return "⏱️ **Fix:** Rate limit hit. Wait 1 minute and try again, or check your quota at https://aistudio.google.com"
    if "not found" in e or "404" in e or "model" in e:
        return "🤖 **Fix:** Model not found. Open `config.yaml` and change `model` to `gemini-1.5-flash` or `gemini-pro`."
    if "network" in e or "connection" in e or "timeout" in e:
        return "🌐 **Fix:** Network error. Check your internet connection and try again."
    if "environment" in e or "gemini_api_key" in e:
        return "🔑 **Fix:** `GEMINI_API_KEY` is not set. Create a `.env` file with `GEMINI_API_KEY=your_key_here`."
    return "📋 **Fix:** Copy the error above and check the Gemini API documentation."


def _render_sidebar(config: dict) -> None:
    """Render the sidebar with session info, debug panel, and controls."""
    with st.sidebar:
        st.title("🎯 CareerAI")
        st.caption(config["app"]["description"])
        st.divider()

        # ── API Status & Debug Panel ─────────────────────────────────
        st.subheader("🔌 API Status")
        if st.session_state.get("api_ready", False):
            st.success("✅ Gemini API Connected")
        else:
            st.error("❌ API Not Connected")
            err = st.session_state.get("api_error", "Unknown error")
            st.code(err, language="text")
            hint = _get_error_hint(err)
            st.info(hint)

            # Re-test button (useful after fixing .env)
            if st.button("🔄 Re-test API Connection", use_container_width=True):
                # Clear cached model so it re-initializes
                for key in ["model", "api_ready", "api_error"]:
                    st.session_state.pop(key, None)
                st.rerun()

        st.divider()

        # ── Session Info ─────────────────────────────────────────────
        if config["ui"]["show_session_info"]:
            session = st.session_state.session
            st.subheader("📊 Session Info")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Messages", get_message_count(session))
            with col2:
                st.metric("Tokens", session.total_tokens_used)
            st.caption(f"Session ID: `{session.session_id}`")
            st.divider()

        # ── Quick Prompts ─────────────────────────────────────────────
        st.subheader("💡 Quick Topics")
        quick_prompts = [
            "Help me improve my resume",
            "How to negotiate salary?",
            "Prepare for a tech interview",
            "Career change advice",
            "Optimize my LinkedIn profile",
        ]
        for prompt in quick_prompts:
            if st.button(f"→ {prompt}", use_container_width=True, key=f"qp_{prompt}"):
                st.session_state.quick_prompt = prompt

        st.divider()

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            clear_session(st.session_state.session)
            st.session_state.messages_display = [
                {"role": "assistant", "content": get_welcome_message()}
            ]
            st.rerun()

        st.caption(f"v{config['app']['version']} | Powered by Gemini")


def _render_chat_messages(config: dict) -> None:
    """Render all messages. Uses only role strings — no emoji avatars."""
    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _handle_user_input(user_input: str, config: dict) -> None:
    """Process user input: display, call API, render response or real error."""
    if not user_input.strip():
        return

    max_turns = config["conversation"]["max_history_turns"]

    # Show user message immediately
    st.session_state.messages_display.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    add_message(st.session_state.session, "user", user_input)

    # Generate response
    with st.chat_message("assistant"):

        # Check API readiness
        if not st.session_state.get("api_ready", False):
            err = st.session_state.get("api_error", "Unknown error")
            hint = _get_error_hint(err)
            st.error(f"**API not ready.** Cannot process your message.\n\n**Error:** `{err}`")
            st.info(hint)
            return

        with st.spinner("CareerAI is thinking..."):
            history = get_history_for_api(st.session_state.session, max_turns)
            history = history[:-1] if history else []

            result = send_message(
                model=st.session_state.model,
                user_message=user_input,
                chat_history=history,
            )

        # ── Success ───────────────────────────────────────────────────
        if result["success"] and result["text"]:
            response_text = result["text"]
            st.markdown(response_text)
            if config["ui"]["show_token_usage"] and result["tokens_used"] > 0:
                st.caption(f"🔢 Tokens used: {result['tokens_used']}")

            st.session_state.messages_display.append(
                {"role": "assistant", "content": response_text}
            )
            add_message(
                st.session_state.session, "model", response_text, result["tokens_used"]
            )
            logger.info(
                f"Turn complete | session={st.session_state.session.session_id} | "
                f"tokens={result['tokens_used']}"
            )

        # ── Failure — show REAL error ─────────────────────────────────
        else:
            error_msg = result.get("error", "Unknown error")
            hint = _get_error_hint(error_msg)
            logger.error(f"API call failed: {error_msg}")

            st.error("**API call failed.** Here is the real error:")
            st.code(error_msg, language="text")
            st.info(hint)
            st.caption("Fix the error above, then click **Re-test API Connection** in the sidebar.")


def render_chat_interface(config: dict) -> None:
    """Main function to render the full chat interface."""
    _init_session_state(config)

    st.title(f"{config['app']['icon']} {config['app']['title']}")
    st.caption("AI-powered career guidance — resume tips, interview prep, job search strategies & more")
    st.divider()

    _render_sidebar(config)
    _render_chat_messages(config)

    if "quick_prompt" in st.session_state:
        quick = st.session_state.pop("quick_prompt")
        _handle_user_input(quick, config)
        st.rerun()

    user_input = st.chat_input("Ask me anything about your career...")
    if user_input:
        _handle_user_input(user_input, config)