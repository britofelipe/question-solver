import streamlit as st
import json
from services.api import API
from components.ui import render_notebook_card

def get_current_notebook_children(notebooks, target_id):
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

def render(navigate_to, navigate_up):
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation")
        if st.button("🏠 Home", use_container_width=True):
             navigate_to("home")
        if st.button("📊 Metrics", use_container_width=True):
             navigate_to("metrics")
        if st.button("🛠️ Tools", use_container_width=True):
             navigate_to("tools")
    
    st.title("📚 Notebooks")
    
    # Breadcrumbs & Navigation
    col_back, col_path = st.columns([1, 10])
    with col_back:
        if st.session_state.breadcrumbs:
            if st.button("⬅ Back"):
                 navigate_up(len(st.session_state.breadcrumbs) - 2)
    
    with col_path:
        path_names = ["Home"] + [b['name'] for b in st.session_state.breadcrumbs]
        st.markdown(f"### {' > '.join(path_names)}")

    all_notebooks = API.get_notebooks()
    current_children = get_current_notebook_children(all_notebooks, st.session_state.current_notebook_id)
    
    # Notebooks Grid
    if current_children:
        cols = st.columns(3)
        
        def on_open(id, name):
            st.session_state.current_notebook_id = id
            st.session_state.breadcrumbs.append({"id": id, "name": name})
            st.rerun()
            
        def on_study(nb):
            st.session_state.selected_notebook_for_study = nb
            navigate_to("study_setup")
            
        def on_delete(id):
            API.delete_notebook(id)
            st.rerun()

        for idx, nb in enumerate(current_children):
            with cols[idx % 3]:
                render_notebook_card(nb, on_open, on_study, on_delete)
    else:
        if not st.session_state.current_notebook_id:
             st.info("No notebooks created yet.")

    # Question Management (Only if inside a notebook)
    if st.session_state.current_notebook_id:
        st.markdown("---")
        st.subheader("📝 Questions in this Notebook")
        
        questions = API.get_questions(st.session_state.current_notebook_id)
        if questions:
            for q in questions:
                with st.expander(f"{q['content'][:50]}... ({q['type']})"):
                    st.write(f"**Question:** {q['content']}")
                    st.write(f"**Answer:** {q['correct_answer']}")
                    if st.button("Delete Question", key=f"del_q_{q['id']}"):
                        if API.delete_question(q['id']):
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
        else:
            st.info("No questions in this notebook.")

        # Upload Section
        st.markdown("---")
        st.subheader("📤 Upload Questions")
        json_input = st.text_area("Paste JSON here", height=150)
        if st.button("Upload"):
            try:
                data = json.loads(json_input)
                res = API.upload_questions(st.session_state.current_notebook_id, data)
                if res.status_code == 200:
                    st.success(f"Successfully uploaded questions!")
                    st.rerun()
                else:
                    st.error("Failed to upload.")
            except json.JSONDecodeError:
                st.error("Invalid JSON format.")

    # Create Notebook (Moved to bottom)
    if st.session_state.current_notebook_id is None or current_children:
        st.markdown("---")
        c1, c2 = st.columns([3, 1])
        with c1:
            new_nb_name = st.text_input("New Notebook Name", placeholder="e.g. History")
        with c2:
            st.write("")
            st.write("")
            if st.button("➕ Create Notebook", use_container_width=True):
                if new_nb_name:
                    API.create_notebook(new_nb_name, st.session_state.current_notebook_id)
                    st.rerun()
