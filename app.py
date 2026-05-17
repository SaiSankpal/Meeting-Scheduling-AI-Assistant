import streamlit as st
import requests
import uuid

# ------------------ CONFIG ------------------

st.set_page_config(page_title="AI Meeting Scheduler", layout="wide")
st.title("📅 Meeting Scheduling AI Assistant")

API_URL = "http://127.0.0.1:8000/chat"

# ------------------ SESSION STATE ------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "show_actions" not in st.session_state:
    st.session_state.show_actions = False

# ------------------ DISPLAY CHAT HISTORY ------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ------------------ USER INPUT ------------------

if prompt := st.chat_input("What would you like to do?"):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Backend call
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                API_URL,
                json={
                    "user_id": st.session_state.user_id,
                    "user_input": prompt
                },
                timeout=120,
            )

            response.raise_for_status()
            result = response.json()

            assistant_reply = result.get("response", "")
            event_link = result.get("event_link")
            status = result.get("status")

            if event_link:
                assistant_reply += f"\n\n🔗 [Open meeting]({event_link})"

            if status == "success":
                st.session_state.show_actions = True
            else:
                st.session_state.show_actions = False

        except requests.exceptions.Timeout:
            assistant_reply = "⏱ Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            assistant_reply = "⚠️ Backend not running. Start FastAPI server."
        except requests.exceptions.RequestException as e:
            assistant_reply = f"❌ Error: {str(e)}"
        except Exception as e:
            assistant_reply = f"⚠️ Unexpected error: {str(e)}"

    # Save assistant reply
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )

    # Detect confirmation stage
    if "confirm" in assistant_reply.lower():
        st.session_state.awaiting_confirmation = True
    else:
        st.session_state.awaiting_confirmation = False

    st.rerun()


# ------------------ CONFIRMATION UI ------------------

if st.session_state.awaiting_confirmation:

    with st.chat_message("assistant"):
        st.markdown("### ✅ Confirm your action")

        col1, col2 = st.columns(2)

        # -------- CONFIRM BUTTON --------
        if col1.button("✅ Confirm", key="confirm_btn"):

            # Show user action in chat
            st.session_state.messages.append(
                {"role": "user", "content": "confirm"}
            )

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "user_id": st.session_state.user_id,
                        "user_input": "Yes"
                    },
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()

                reply = result.get("response", "")
                event_link = result.get("event_link")

                if event_link:
                    reply += f"\n\n🔗 [Open calendar event]({event_link})"

            except requests.exceptions.Timeout:
                reply = "⏱ Confirmation timed out."
            except requests.exceptions.RequestException as e:
                reply = f"❌ Error: {str(e)}"

            # Show assistant reply
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            st.session_state.awaiting_confirmation = False
            st.rerun()

        # -------- CHANGE BUTTON --------
        if col2.button("❌ Change", key="change_btn"):

            st.session_state.messages.append(
                {"role": "user", "content": "change"}
            )

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "user_id": st.session_state.user_id,
                        "user_input": "No"
                    },
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()

                reply = result.get("response", "")
                event_link = result.get("event_link")

                if event_link:
                    reply += f"\n\n🔗 [Open calendar event]({event_link})"

            except requests.exceptions.Timeout:
                reply = "⏱ Change request timed out."
            except requests.exceptions.RequestException as e:
                reply = f"❌ Error: {str(e)}"

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            st.session_state.awaiting_confirmation = False
            st.rerun()

# ------------------ POST-SCHEDULING ACTIONS ------------------

if st.session_state.show_actions:

    with st.chat_message("assistant"):
        st.markdown("### What would you like to do next?")

        col1, col2 = st.columns(2)

        # 🔄 RESCHEDULE BUTTON
        if col1.button("🔄 Reschedule", key="reschedule_btn"):

            st.session_state.messages.append(
                {"role": "user", "content": "reschedule"}
            )

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "user_id": st.session_state.user_id,
                        "user_input": "reschedule"
                    },
                    timeout=120,
                )
                result = response.json()
                reply = result.get("response", "")

            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            st.session_state.show_actions = False
            st.rerun()

        # ❌ CANCEL BUTTON
        if col2.button("❌ Cancel", key="cancel_btn"):

            st.session_state.messages.append(
                {"role": "user", "content": "cancel"}
            )

            try:
                response = requests.post(
                    API_URL,
                    json={
                        "user_id": st.session_state.user_id,
                        "user_input": "cancel"
                    },
                    timeout=120,
                )
                result = response.json()
                reply = result.get("response", "")

            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            st.session_state.show_actions = False
            st.rerun()