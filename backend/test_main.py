import os
# Set dummy env var before importing database module to avoid crash
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from main import app
from app.core.database import get_session
from app.models import Notebook, Question, Attempt

# Use an in-memory SQLite database for testing
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture():
    create_db_and_tables()
    with Session(engine) as session:
        yield session
    drop_db_and_tables()

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# --- Tests (Same logic, slightly updated imports handled above) ---

def test_read_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Question Solver API is running"}

def test_notebook_lifecycle(client: TestClient):
    # 1. Create Root Notebook
    res = client.post("/notebooks/", json={"name": "Science"})
    assert res.status_code == 200
    root_id = res.json()["id"]
    assert res.json()["name"] == "Science"
    assert res.json()["parent_id"] is None

    # 2. Create Sub Notebook
    res = client.post("/notebooks/", json={"name": "Physics", "parent_id": root_id})
    assert res.status_code == 200
    sub_id = res.json()["id"]
    assert res.json()["parent_id"] == root_id

    # 3. Create Sub-Sub Notebook
    res = client.post("/notebooks/", json={"name": "Quantum Mechanics", "parent_id": sub_id})
    assert res.status_code == 200
    subsub_id = res.json()["id"]

    # 4. Read Tree
    res = client.get("/notebooks/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "Science"
    assert len(data[0]["sub_notebooks"]) == 1
    assert data[0]["sub_notebooks"][0]["name"] == "Physics"
    assert len(data[0]["sub_notebooks"][0]["sub_notebooks"]) == 1
    assert data[0]["sub_notebooks"][0]["sub_notebooks"][0]["name"] == "Quantum Mechanics"

    # 5. Delete Notebook
    res = client.delete(f"/notebooks/{root_id}")
    assert res.status_code == 200
    res = client.get("/notebooks/")
    assert res.json() == []

def test_question_flow(client: TestClient):
    # Setup: Create notebook
    res = client.post("/notebooks/", json={"name": "Math"})
    nb_id = res.json()["id"]

    # 1. Upload Questions
    questions_payload = {
        "questions": [
            {
                "content": "2 + 2 = ?",
                "type": "multiple_choice",
                "language": "en",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "explanation": "Simple arithmetic."
            },
            {
                "content": "Is the earth flat?",
                "type": "true_false",
                "language": "en",
                "options": ["True", "False"],
                "correct_answer": "False",
                "explanation": "It is spherical."
            }
        ]
    }
    res = client.post(f"/questions/upload/{nb_id}", json=questions_payload)
    assert res.status_code == 200
    assert "Imported 2 questions" in res.json()["message"]

    # 2. Study: Get All
    res = client.get(f"/study/{nb_id}?mode=all")
    assert res.status_code == 200
    questions = res.json()
    assert len(questions) == 2
    
    # 3. Study: Attempt Correct
    q_math = next(q for q in questions if q["content"] == "2 + 2 = ?")
    res = client.post("/attempt/", json={"question_id": q_math["id"], "selected_option": "4"})
    assert res.status_code == 200
    assert res.json()["is_correct"] is True

    # 4. Study: Attempt Incorrect
    q_earth = next(q for q in questions if q["content"] == "Is the earth flat?")
    res = client.post("/attempt/", json={"question_id": q_earth["id"], "selected_option": "True"}) 
    assert res.status_code == 200
    assert res.json()["is_correct"] is False

    # 5. Stats
    res = client.get(f"/stats/{nb_id}")
    stats = res.json()
    assert stats["total_questions"] == 2
    assert stats["attempted"] == 2
    assert stats["correct"] == 1
    assert stats["incorrect"] == 1
    assert stats["accuracy"] == 0.5

def test_pdf_split(client: TestClient):
    # Create a dummy PDF in memory
    from pypdf import PdfWriter
    import io
    
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100) # Page 1
    writer.add_blank_page(width=100, height=100) # Page 2
    writer.add_blank_page(width=100, height=100) # Page 3
    
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    
    # Send to API
    files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
    data = {"chunk_size": 2}
    
    res = client.post("/tools/split-pdf", files=files, data=data)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    
    # Verify ZIP content
    import zipfile
    zip_buffer = io.BytesIO(res.content)
    with zipfile.ZipFile(zip_buffer, "r") as z:
        # Should have split into 2 files: 1-2 (2 pages) and 3-3 (1 page)
        assert len(z.namelist()) == 2
        assert "split_1-2.pdf" in z.namelist()
        assert "split_3-3.pdf" in z.namelist()
