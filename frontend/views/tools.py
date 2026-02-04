import streamlit as st
from services.api import API
import requests
import os

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def render(navigate_to):
    st.title("🛠️ Tools")
    st.markdown("### 📄 PDF Splitter")
    st.write("Upload a PDF to split it into smaller chunks for LLM processing.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    chunk_size = st.number_input("Pages per chunk", min_value=1, value=5)
    
    if uploaded_file and st.button("Split PDF"):
        with st.spinner("Processing..."):
            try:
                # Using requests directly here as multipart upload needs specific handling
                # or add method to API class
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                data = {"chunk_size": chunk_size}
                
                res = requests.post(f"{API_URL}/tools/split-pdf", files=files, data=data)
                
                if res.status_code == 200:
                    st.success("PDF Split Successfully!")
                    st.download_button(
                        label="⬇️ Download Split Files (ZIP)",
                        data=res.content,
                        file_name="split_files.zip",
                        mime="application/zip"
                    )
                else:
                    st.error(f"Failed to split PDF: {res.text}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
                
    st.markdown("---")
    if st.button("← Back to Home"):
        navigate_to("home")
