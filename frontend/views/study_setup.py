import streamlit as st
from services.api import API
import plotly.express as px
import pandas as pd

def render(navigate_to):
    nb = st.session_state.get("selected_notebook_for_study")
    if not nb:
        navigate_to("home")
        return

    st.title(f"📖 Study: {nb['name']}")
    
    if st.button("← Back"):
        navigate_to("home")
        
    # Stats Visualization
    stats = API.get_stats(nb['id'])
    
    col_chart, col_config = st.columns([1, 1])
    
    with col_chart:
        pending = stats['total_questions'] - stats['attempted']
        data = {
            "Status": ["Correct", "Incorrect", "Pending"],
            "Count": [stats['correct'], stats['incorrect'], pending]
        }
        df = pd.DataFrame(data)
        fig = px.pie(df, values='Count', names='Status', title=f"Progress: {nb['name']}",
                     color='Status',
                     color_discrete_map={'Correct':'#10B981', 'Incorrect':'#EF4444', 'Pending':'#6B7280'},
                     height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_config:
        st.subheader("Session Configuration")
        mode = st.selectbox("Mode", ["all", "incorrect", "unresolved"], format_func=lambda x: x.capitalize())
        randomize = st.checkbox("Randomize Order", value=True)
        
        st.write("")
        if st.button("Start Session", type="primary", use_container_width=True):
            questions = API.get_study_questions(nb['id'], mode, randomize)
            if not questions:
                st.warning("No questions found for this criteria.")
            else:
                st.session_state.study_queue = questions
                st.session_state.current_question_index = 0
                navigate_to("study_session")
            
    # Quick Stats Text
    st.markdown("### Details")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", stats['total_questions'])
    col2.metric("Accuracy", f"{stats['accuracy']*100:.1f}%")
    col3.metric("Pending", stats['total_questions'] - stats['attempted'])
