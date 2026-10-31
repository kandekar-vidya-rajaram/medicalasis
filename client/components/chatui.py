import streamlit as st
import requests
from client.utils.api import ask_question


def render_chat():
    st.subheader("💬 Chat with your assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_input = st.chat_input("Type your question...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            with st.spinner("Searching your PDF..."):
                response = ask_question(user_input)

            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")

                if not answer:
                    answer = "No answer was returned by the backend."

                with st.chat_message("assistant"):
                    st.markdown(answer)

                    sources = data.get("sources", [])
                    if sources:
                        with st.expander("📄 Sources"):
                            for src in sources:
                                st.write(src)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            else:
                try:
                    error_message = response.json().get(
                        "error", response.text
                    )
                except ValueError:
                    error_message = response.text

                st.error(f"API Error: {error_message}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")

        except requests.exceptions.RequestException as error:
            st.error(f"Could not reach the assistant API: {error}")

        except (ValueError, KeyError) as error:
            st.error(f"Invalid API response: {error}")
