import streamlit as st
from services.api import API
import plotly.express as px
import pandas as pd

def render(navigate_to):
    st.title("📊 Metrics Dashboard")
    
    # Global Stats
    global_stats = API.get_global_stats()
    
    st.markdown("### Global Performance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Questions", global_stats['total_questions'])
    c2.metric("Attempted", global_stats['attempted'])
    c3.metric("Accuracy", f"{global_stats['accuracy']*100:.1f}%")
    
    pending = global_stats['total_questions'] - global_stats['attempted']
    c4.metric("Pending", pending)
    
    st.markdown("---")
    
    col_chart, col_breakdown = st.columns([1, 2])
    
    with col_chart:
        # Pie Chart
        data = {
            "Status": ["Correct", "Incorrect", "Pending"],
            "Count": [global_stats['correct'], global_stats['incorrect'], pending]
        }
        df = pd.DataFrame(data)
        fig = px.pie(df, values='Count', names='Status', title='Overall Progress', 
                     color='Status',
                     color_discrete_map={'Correct':'#10B981', 'Incorrect':'#EF4444', 'Pending':'#6B7280'})
        st.plotly_chart(fig, use_container_width=True)

    with col_breakdown:
        st.subheader("Notebook Performance")
        # Get all root notebooks for breakdown
        notebooks = API.get_notebooks()
        
        nb_data = []
        for nb in notebooks:
            stats = API.get_stats(nb['id'])
            nb_data.append({
                "Notebook": nb['name'],
                "Accuracy": stats['accuracy'],
                "Questions": stats['total_questions']
            })
            
        if nb_data:
            df_nb = pd.DataFrame(nb_data)
            fig_bar = px.bar(df_nb, x='Notebook', y='Accuracy', title='Accuracy per Notebook',
                             color='Accuracy', color_continuous_scale='Bluered_r', range_y=[0, 1])
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No notebooks available for breakdown.")

    if st.button("← Back to Home"):
        navigate_to("home")
