import streamlit as st
from frontend.services.api import API

def render(navigate_to):
    nb = st.session_state.get("selected_notebook_for_study")
    if not nb:
        navigate_to("home")
        return

    st.title(f"📖 Study: {nb['name']}")
    
    if st.button("← Back"):
        navigate_to("home")
        
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
            navigate_to("study_session")
            
    # Stats Preview
    stats = API.get_stats(nb['id'])
    st.markdown("### Quick Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", stats['total_questions'])
    col2.metric("Accuracy", f"{stats['accuracy']*100:.1f}%")
    col3.metric("Pending", stats['total_questions'] - stats['attempted'])
