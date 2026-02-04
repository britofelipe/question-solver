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
    
    st.markdown("### ⏱️ Activity")
    c_today, c_week, c_month, c_avg = st.columns(4)
    c_today.metric("Questions Today", global_stats.get('questions_today', 0))
    c_week.metric("Questions this Week", global_stats.get('questions_week', 0))
    c_month.metric("Questions this Month", global_stats.get('questions_month', 0))
    # Placeholder for average time if implemented later
    # c_avg.metric("Avg Time", "N/A") 

    st.markdown("---")
    
    col_chart, col_breakdown = st.columns([1, 1])
    
    with col_chart:
        st.subheader("Global Process")
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
        st.subheader("Activity by Category")
        cat_stats = global_stats.get('category_stats', {})
        if cat_stats:
            df_cat = pd.DataFrame(list(cat_stats.items()), columns=['Category', 'Questions'])
            fig_bar_cat = px.bar(df_cat, x='Category', y='Questions', title='Questions Answered per Category',
                                 color='Questions', color_continuous_scale='Viridis')
            st.plotly_chart(fig_bar_cat, use_container_width=True)
        else:
             st.info("No activity recorded yet.")

    st.markdown("---")
    st.subheader("Notebook Performance (Accuracy)")
    
    # Helper to flatten notebooks
    def get_all_notebooks_flat(nodes):
        flat = []
        for node in nodes:
            flat.append(node)
            if node.get('sub_notebooks'):
                flat.extend(get_all_notebooks_flat(node['sub_notebooks']))
        return flat

    notebooks_tree = API.get_notebooks()
    all_notebooks = get_all_notebooks_flat(notebooks_tree)
    
    nb_data = []
    for nb in all_notebooks:
        stats = API.get_stats(nb['id'])
        # Only show notebooks that have had some activity or questions to reduce clutter
        # Or at least show all. Let's show all for now.
        if stats['total_questions'] > 0:
            nb_data.append({
                "Notebook": nb['name'],
                "Accuracy": stats['accuracy'] * 100, # Scale to 0-100
                "Questions": stats['total_questions']
            })
        
    if nb_data:
        df_nb = pd.DataFrame(nb_data)
        fig_bar = px.bar(df_nb, x='Notebook', y='Accuracy', title='Accuracy per Notebook (%)',
                         color='Accuracy', color_continuous_scale='Bluered_r', range_y=[0, 100],
                         text_auto='.1f')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No notebook activity to display.")

    if st.button("← Back to Home"):
        navigate_to("home")
