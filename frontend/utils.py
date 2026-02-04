import streamlit as st
import requests
import os

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def load_css():
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* General App Styling */
        .stApp {
            font-family: 'Inter', sans-serif;
            background-color: #0E1117; /* Dark background */
            color: #FAFAFA;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161B22;
        }

        /* Headings */
        h1, h2, h3 {
            color: #FFFFFF; 
            font-weight: 700;
        }

        /* Custom Cards for Notebooks */
        .notebook-card {
            background-color: #1F2937;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #374151;
            margin-bottom: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }
        .notebook-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-color: #60A5FA;
        }

        /* Buttons */
        .stButton button {
            background-color: #2563EB;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            border: none;
            font-weight: 600;
        }
        .stButton button:hover {
            background-color: #1D4ED8;
            color: white;
        }

        /* Success/Error Messages */
        .success-box {
            padding: 15px;
            background-color: #064E3B; /* Green-900 */
            color: #D1FAE5;
            border-radius: 8px;
            border-left: 5px solid #10B981;
            margin-bottom: 10px;
        }
        .error-box {
            padding: 15px;
            background-color: #7F1D1D; /* Red-900 */
            color: #FEE2E2;
            border-radius: 8px;
            border-left: 5px solid #EF4444;
            margin-bottom: 10px;
        }
        
        /* Question Card */
        .question-card {
            background-color: #1F2937;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #374151;
            margin-bottom: 20px;
        }
        .option-container {
            margin-top: 15px;
        }
        
        </style>
    """, unsafe_allow_html=True)

# API Wrapper Classes
class API:
    @staticmethod
    def get_notebooks():
        try:
            res = requests.get(f"{API_URL}/notebooks/")
            if res.status_code == 200:
                return res.json()
            return []
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
            return []

    @staticmethod
    def create_notebook(name, parent_id=None):
        payload = {"name": name, "parent_id": parent_id}
        res = requests.post(f"{API_URL}/notebooks/", json=payload)
        return res.json()

    @staticmethod
    def delete_notebook(notebook_id):
        res = requests.delete(f"{API_URL}/notebooks/{notebook_id}")
        return res.status_code == 200

    @staticmethod
    def upload_questions(notebook_id, questions_json):
        res = requests.post(f"{API_URL}/questions/upload/{notebook_id}", json=questions_json)
        return res

    @staticmethod
    def get_study_questions(notebook_id, mode="all", randomize=False):
        params = {"mode": mode, "randomize": randomize}
        res = requests.get(f"{API_URL}/study/{notebook_id}", params=params)
        return res.json()

    @staticmethod
    def submit_attempt(question_id, selected_option):
        payload = {"question_id": question_id, "selected_option": selected_option}
        res = requests.post(f"{API_URL}/attempt/", json=payload)
        return res.json()

    @staticmethod
    def get_stats(notebook_id):
        res = requests.get(f"{API_URL}/stats/{notebook_id}")
        return res.json()
