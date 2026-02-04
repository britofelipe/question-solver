import requests
import os
import streamlit as st

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
        res = requests.get(f"{API_URL}/questions/study/{notebook_id}", params=params)
        return res.json()

    @staticmethod
    def submit_attempt(question_id, selected_option):
        payload = {"question_id": question_id, "selected_option": selected_option}
        res = requests.post(f"{API_URL}/questions/attempt/", json=payload)
        return res.json()

    @staticmethod
    def get_stats(notebook_id):
        res = requests.get(f"{API_URL}/stats/{notebook_id}")
        return res.json()
