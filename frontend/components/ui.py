import streamlit as st
from services.api import API

def render_notebook_card(notebook, on_click_open, on_click_study, on_click_delete):
    with st.container():
        st.markdown(f"""
        <div class="notebook-card">
            <h3>📁 {notebook['name']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Open", key=f"open_{notebook['id']}"):
                on_click_open(notebook['id'], notebook['name'])
        with b2:
            if st.button("Study", key=f"study_{notebook['id']}"):
                on_click_study(notebook)
        with b3:
            with st.popover("🗑", help="Delete Notebook"):
                st.write("Are you sure you want to delete this notebook?")
                st.warning("This action cannot be undone.")
                if st.button("Confirm Delete", key=f"conf_del_{notebook['id']}", type="primary"):
                    on_click_delete(notebook['id'])
    st.write("") 

def render_question_card(question, index, total):
    st.progress((index) / total)
    st.caption(f"Question {index + 1} of {total}")
    
    st.markdown(f"""
    <div class="question-card">
        <h3>{question['content']}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_result_message(is_correct, explanation):
    if is_correct:
        st.markdown(f"""<div class="success-box">✅ Correct! Excellent work.</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="error-box">❌ Incorrect.</div>""", unsafe_allow_html=True)
        
    st.markdown(f"### Explanation")
    st.info(explanation)
