import streamlit as st
from frontend.services.api import API
from frontend.components.ui import render_question_card, render_result_message

def render(navigate_to):
    questions = st.session_state.get("study_queue", [])
    idx = st.session_state.get("current_question_index", 0)
    
    if idx >= len(questions):
        st.success("🎉 You have completed this session!")
        if st.button("Return Home"):
            navigate_to("home")
        return

    q = questions[idx]
    
    render_question_card(q, idx, len(questions))
    
    # State management for current question
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
        render_result_message(result['is_correct'], result['explanation'])
        
        if st.button("Next Question →"):
            st.session_state.current_question_index += 1
            st.rerun()
