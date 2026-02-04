import streamlit as st
from services.api import API
import plotly.express as px
import pandas as pd

def render(navigate_to):
    nb = st.session_state.get("selected_notebook_for_study")
    context_name = st.session_state.get("study_context_name", nb.get('name') if nb else "Unknown")
    
    if not nb:
        navigate_to("home")
        return

    st.title(f"📖 Study: {context_name}")
    
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
        # Default to "unresolved" (index 2)
        mode = st.selectbox("Mode", ["all", "incorrect", "unresolved"], index=2, format_func=lambda x: x.capitalize())
        # Default randomize to False
        randomize = st.checkbox("Randomize Order", value=False)
        
        st.write("")
        if st.button("Start Session", type="primary", use_container_width=True):
            questions = API.get_study_questions(nb['id'], mode, randomize)
            if not questions:
                st.warning("No questions found for this criteria.")
            else:
                st.session_state.study_queue = questions
                st.session_state.current_question_index = 0
                navigate_to("study_session")
                # Ensure rerun happens if navigate_to doesn't trigger it immediately (though it should)
                # It seems in some streamlit versions/contexts updates to session state 
                # inside buttons might not persist if page change happens too fast? 
                # Actually, navigate_to calls rerun. 
                # Let's clean up old session state vars just in case.
                keys_to_clear = [k for k in st.session_state.keys() if k.startswith("answered_") or k.startswith("result_")]
                for k in keys_to_clear:
                    del st.session_state[k]
            
    # Quick Stats Text
    st.markdown("### Details")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", stats['total_questions'])
    col2.metric("Accuracy", f"{stats['accuracy']*100:.1f}%")
    col3.metric("Pending", stats['total_questions'] - stats['attempted'])
