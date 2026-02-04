import streamlit as st
import json
import pandas as pd
import plotly.express as px
from utils import load_css, API

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
if "study_mode_active" not in st.session_state:
    st.session_state.study_mode_active = False

# --- Helper Functions ---

def navigate_to_notebook(notebook_id, name):
    st.session_state.current_notebook_id = notebook_id
    if notebook_id is not None:
        # Avoid duplicate breadcrumbs if navigating up/down logic is complex, 
        # but for drill down, just append. 
        # For managing going back, we might need to truncate.
        # Simple approach: If drilling down, append. If going to root, clear.
        st.session_state.breadcrumbs.append({"id": notebook_id, "name": name})
    else:
        st.session_state.breadcrumbs = []
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

def get_current_notebook_children(notebooks):
    # Recursive search for current children
    target_id = st.session_state.current_notebook_id
    
    if target_id is None:
        return notebooks
    
    def find_node(nodes, target):
        for node in nodes:
            if node['id'] == target:
                return node.get('sub_notebooks', [])
            res = find_node(node.get('sub_notebooks', []), target)
            if res is not None:
                return res
        return None

    return find_node(notebooks, target_id) or []

# --- Views ---

def home_view():
    st.title("📚 Notebooks")
    
    # Breadcrumbs
    cols = st.columns([1, 8])
    with cols[0]:
        if st.button("🏠 Home", key="crumb_root"):
            navigate_up(-1)
    
    with cols[1]:
        crumb_str = " > ".join([b['name'] for b in st.session_state.breadcrumbs])
        if crumb_str:
            st.markdown(f"**Path:** {crumb_str}")

    all_notebooks = API.get_notebooks()
    current_children = get_current_notebook_children(all_notebooks)
    
    # Action Bar
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        new_nb_name = st.text_input("New Notebook Name", placeholder="e.g. Mathematics")
    with c2:
        st.write("") 
        if st.button("➕ Create Notebook", use_container_width=True):
            if new_nb_name:
                API.create_notebook(new_nb_name, st.session_state.current_notebook_id)
                st.rerun()
    
    st.markdown("---")
    
    if not current_children:
        st.info("No notebooks here. Create one or upload questions!")
    
    # Grid Layout for Notebooks
    cols = st.columns(3)
    for idx, nb in enumerate(current_children):
        with cols[idx % 3]:
            # Card-like container
            with st.container():
                st.markdown(f"""
                <div class="notebook-card">
                    <h3>📁 {nb['name']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("Open", key=f"open_{nb['id']}"):
                        navigate_to_notebook(nb['id'], nb['name'])
                with b2:
                    if st.button("Study", key=f"study_{nb['id']}"):
                        st.session_state.selected_notebook_for_study = nb
                        st.session_state.page = "study_setup"
                        st.rerun()
                with b3:
                    if st.button("🗑", key=f"del_{nb['id']}"):
                        API.delete_notebook(nb['id'])
                        st.rerun()
            st.write("") # Spacer

    # Upload Section for Current Level
    st.markdown("---")
    st.subheader("📤 Upload Questions to Current Location")
    
    target_nb_name = st.session_state.breadcrumbs[-1]['name'] if st.session_state.breadcrumbs else "Root (Please select a notebook first)"
    st.markdown(f"Uploading to: **{target_nb_name}**")
    
    if st.session_state.current_notebook_id:
        json_input = st.text_area("Paste JSON here", height=200)
        if st.button("Upload Questions"):
            try:
                data = json.loads(json_input)
                res = API.upload_questions(st.session_state.current_notebook_id, data)
                if res.status_code == 200:
                    st.success(f"Successfully uploaded questions!")
                else:
                    st.error("Failed to upload.")
            except json.JSONDecodeError:
                st.error("Invalid JSON format.")
    else:
        st.warning("You must enter a notebook to upload questions.")

def study_setup_view():
    nb = st.session_state.selected_notebook_for_study
    st.title(f"📖 Study: {nb['name']}")
    
    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()
        
    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("Mode", ["all", "incorrect", "unresolved"], format_func=lambda x: x.capitalize())
    with c2:
        randomize = st.checkbox("Randomize Order", value=True)
        
    if st.button("Start Session", type="primary"):
        questions = API.get_study_questions(nb['id'], mode, randomize)
        if not questions:
            st.warning("No questions found for this criteria.")
        else:
            st.session_state.study_queue = questions
            st.session_state.current_question_index = 0
            st.session_state.page = "study_session"
            st.rerun()
            
    # Stats Preview
    stats = API.get_stats(nb['id'])
    st.markdown("### Quick Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", stats['total_questions'])
    col2.metric("Accuracy", f"{stats['accuracy']*100:.1f}%")
    col3.metric("Pending", stats['total_questions'] - stats['attempted'])

def study_session_view():
    questions = st.session_state.study_queue
    idx = st.session_state.current_question_index
    
    if idx >= len(questions):
        st.success("🎉 You have completed this session!")
        if st.button("Return Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    q = questions[idx]
    
    st.progress((idx) / len(questions))
    st.caption(f"Question {idx + 1} of {len(questions)}")
    
    # Question Card
    st.markdown(f"""
    <div class="question-card">
        <h3>{q['content']}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Options
    # We use a key based on index to reset state between questions
    
    # Check if we already answered this specifc instance in session? 
    # For simplicity, session state for loop.
    
    if f"answered_{idx}" not in st.session_state:
        st.session_state[f"answered_{idx}"] = False
        st.session_state[f"result_{idx}"] = None

    answered = st.session_state[f"answered_{idx}"]
    result = st.session_state[f"result_{idx}"]

    if not answered:
        selected = st.radio("Choose your answer:", q['options'], key=f"q_{idx}")
        if st.button("Confirm Answer"):
            res = API.submit_attempt(q['id'], selected)
            st.session_state[f"result_{idx}"] = res
            st.session_state[f"answered_{idx}"] = True
            st.rerun()
    else:
        # Show Result
        res = result
        if res['is_correct']:
            st.markdown(f"""<div class="success-box">✅ Correct! Excellent work.</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="error-box">❌ Incorrect.</div>""", unsafe_allow_html=True)
            
        st.markdown(f"### Explanation")
        st.info(res['explanation'])
        
        if st.button("Next Question →"):
            st.session_state.current_question_index += 1
            st.rerun()

# --- Main Router ---

if st.session_state.page == "home":
    home_view()
elif st.session_state.page == "study_setup":
    study_setup_view()
elif st.session_state.page == "study_session":
    study_session_view()
