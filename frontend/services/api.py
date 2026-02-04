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
        try:
            params = {"mode": mode, "randomize": randomize}
            # Route is /study/{id}, not /questions/study/{id}
            res = requests.get(f"{API_URL}/study/{notebook_id}", params=params)
            if res.status_code == 200:
                return res.json()
            st.error(f"Backend Error ({res.status_code}): {res.text}")
            return []
        except Exception as e:
            st.error(f"Connection Error: {e}")
            return []

    @staticmethod
    def submit_attempt(question_id, selected_option):
        try:
            payload = {"question_id": question_id, "selected_option": selected_option}
            # Route is /attempt/, not /questions/attempt/
            res = requests.post(f"{API_URL}/attempt/", json=payload)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    @staticmethod
    def get_stats(notebook_id):
        try:
            res = requests.get(f"{API_URL}/stats/{notebook_id}")
            if res.status_code == 200:
                return res.json()
            # Return default stats on failure
            return {
                "total_questions": 0,
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0.0
            }
        except Exception:
            return {
                "total_questions": 0,
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0.0
            }

    @staticmethod
    def get_global_stats():
        try:
            res = requests.get(f"{API_URL}/stats/global")
            if res.status_code == 200:
                return res.json()
            return {
                "total_questions": 0,
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0.0
            }
        except Exception:
            return {
                "total_questions": 0,
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0.0
            }

    @staticmethod
    def get_questions(notebook_id):
        try:
            res = requests.get(f"{API_URL}/questions/notebook/{notebook_id}")
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    @staticmethod
    def delete_question(question_id):
        try:
             res = requests.delete(f"{API_URL}/questions/{question_id}")
             return res.status_code == 200
        except Exception:
             return False
