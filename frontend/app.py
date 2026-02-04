import streamlit as st
from frontend.utils.styles import load_css
from frontend.views import home, study_setup, study_session

# Page Configuration
st.set_page_config(page_title="QuestMaster", page_icon="📚", layout="wide")
load_css()

# Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "home"
if "current_notebook_id" not in st.session_state:
    st.session_state.current_notebook_id = None # Root
if "breadcrumbs" not in st.session_state:
    st.session_state.breadcrumbs = [] # List of {"id": int, "name": str}
if "study_queue" not in st.session_state:
    st.session_state.study_queue = []
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0

# --- Router Functions ---

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def navigate_up(index):
    # Navigate to a specific breadcrumb index
    if index == -1: # Root
        st.session_state.current_notebook_id = None
        st.session_state.breadcrumbs = []
    else:
        target = st.session_state.breadcrumbs[index]
        st.session_state.current_notebook_id = target["id"]
        st.session_state.breadcrumbs = st.session_state.breadcrumbs[:index+1]
    st.rerun()

# --- Main App ---

if st.session_state.page == "home":
    home.render(navigate_to, navigate_up)
elif st.session_state.page == "study_setup":
    study_setup.render(navigate_to)
elif st.session_state.page == "study_session":
    study_session.render(navigate_to)
