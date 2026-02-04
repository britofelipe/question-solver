import streamlit as st
import json
from frontend.services.api import API
from frontend.components.ui import render_notebook_card

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
    current_children = get_current_notebook_children(all_notebooks, st.session_state.current_notebook_id)
    
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
    
    # Grid Layout
    cols = st.columns(3)
    
    # Callback wrappers
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
            
    # Upload Section
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
