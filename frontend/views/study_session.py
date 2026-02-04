import streamlit as st
from services.api import API
from components.ui import render_question_card, render_result_message

def render(navigate_to):
    questions = st.session_state.get("study_queue", [])
    idx = st.session_state.get("current_question_index", 0)
    
    if idx >= len(questions):
        st.success("🎉 You have completed this session!")
        if st.button("Return Home"):
            navigate_to("home")
        return

    q = questions[idx]
    
    # Context Header
    context_name = st.session_state.get("study_context_name", "")
    if context_name:
        st.caption(f"📖 Study: {context_name}")

    # Header with actions
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1:
        st.subheader(f"Question {idx + 1} of {len(questions)}")
    
    with c2:
        if st.button("⏹ Stop", help="Exit Session"):
            navigate_to("study_setup")
            
    with c3:
        if st.button("🗑 Delete", key=f"del_study_{q['id']}", help="Delete Question"):
            if API.delete_question(q['id']):
                questions.pop(idx)
                st.session_state.study_queue = questions
                if f"answered_{idx}" in st.session_state:
                     del st.session_state[f"answered_{idx}"]
                if f"result_{idx}" in st.session_state:
                     del st.session_state[f"result_{idx}"]
                
                st.toast("Deleted")
                st.rerun()
    
    render_question_card(q, idx, len(questions))
    
    # State management for current question
    # Note: If we shuffle, IDs are better keys, but index is simple for now. 
    # With delete separate, using index can be tricky if not cleared.
    # Let's use q['id'] for state keys to be safe against shifts
    
    q_key = f"q_{q['id']}"
    
    if f"answered_{q_key}" not in st.session_state:
        st.session_state[f"answered_{q_key}"] = False
        st.session_state[f"result_{q_key}"] = None

    answered = st.session_state[f"answered_{q_key}"]
    result = st.session_state[f"result_{q_key}"]

    if not answered:
        selected = st.radio("Choose your answer:", q['options'], key=f"radio_{q_key}")
        if st.button("Confirm Answer"):
            res = API.submit_attempt(q['id'], selected)
            st.session_state[f"result_{q_key}"] = res
            st.session_state[f"answered_{q_key}"] = True
            st.rerun()
    else:
        render_result_message(result['is_correct'], result['explanation'])
        
        if st.button("Next Question →"):
            st.session_state.current_question_index += 1
            st.rerun()
