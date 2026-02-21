import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Enterprise AI Assistant", layout="centered")
st.title("🔒 Enterprise AI Document Assistant")

# --- Session State Initialization ---
if "token" not in st.session_state:
    st.session_state["token"] = None

# --- UI: Login Screen ---
if not st.session_state["token"]:
    st.info("Please log in to access the secure AI backend.")
    with st.form("login_form"):
        username = st.text_input("Username (Email)")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            # FastAPI OAuth2 expects form data, not JSON
            login_data = {"username": username, "password": password}
            response = requests.post(f"{API_URL}/login", data=login_data)
            
            if response.status_code == 200:
                st.session_state["token"] = response.json().get("access_token")
                st.success("Login successful! Loading AI engine...")
                st.rerun()
            else:
                st.error("Invalid credentials. Are you sure the backend is running?")

# --- UI: AI Application (Only visible if logged in) ---
else:
    st.success("Authenticated as Admin. JWT Token Active.")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    if st.button("Logout"):
        st.session_state["token"] = None
        st.rerun()

    st.divider()

    # Layout with two columns
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("1. Knowledge Base")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        
        if st.button("Ingest to ChromaDB"):
            if uploaded_file:
                with st.spinner("Processing vectors..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    # Notice we pass the secure headers here!
                    response = requests.post(f"{API_URL}/chat/ingest", files=files, headers=headers)
                    if response.status_code == 200:
                        st.success("Ingested successfully!")
                    else:
                        st.error(f"Error {response.status_code}: Failed to ingest.")
            else:
                st.warning("Upload a file first.")

    with col2:
        st.header("2. AI Query Engine")
        user_query = st.text_area("Ask the document a question:")
        
        if st.button("Generate Answer"):
            if user_query:
                with st.spinner("Searching database & generating response..."):
                    response = requests.post(
                        f"{API_URL}/chat/ask", 
                        params={"query": user_query}, 
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.info(response.json())
                    else:
                        st.error(f"Error {response.status_code}: AI failed to respond.")
            else:
                st.warning("Enter a query first.")