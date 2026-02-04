import os
# Set dummy env var before importing database module to avoid crash
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from main import app, get_session, Notebook, Question, Attempt

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

# --- Tests ---

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
    # Should be hierarchical
    # [ {id: 1, name: Science, sub_notebooks: [ {id: 2, name: Physics, sub: ...} ]} ]
    assert len(data) == 1
    assert data[0]["name"] == "Science"
    assert len(data[0]["sub_notebooks"]) == 1
    assert data[0]["sub_notebooks"][0]["name"] == "Physics"
    assert len(data[0]["sub_notebooks"][0]["sub_notebooks"]) == 1
    assert data[0]["sub_notebooks"][0]["sub_notebooks"][0]["name"] == "Quantum Mechanics"

    # 5. Delete Notebook
    res = client.delete(f"/notebooks/{root_id}")
    assert res.status_code == 200
    # Verify deletion (API returns empty list now)
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
    q1_id = questions[0]["id"]
    q2_id = questions[1]["id"]

    # 3. Study: Attempt Correct
    # Assume Q1 is 2+2 (but order might vary if randomized default, so check content)
    # The fixture resets DB, so ID 1 should be the first inserted usually.
    # Let's find "2 + 2 = ?"
    q_math = next(q for q in questions if q["content"] == "2 + 2 = ?")
    
    res = client.post("/attempt/", json={"question_id": q_math["id"], "selected_option": "4"})
    assert res.status_code == 200
    assert res.json()["is_correct"] is True

    # 4. Study: Attempt Incorrect
    q_earth = next(q for q in questions if q["content"] == "Is the earth flat?")
    res = client.post("/attempt/", json={"question_id": q_earth["id"], "selected_option": "True"}) # Wrong
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

    # 6. Study: Filter "incorrect"
    res = client.get(f"/study/{nb_id}?mode=incorrect")
    data = res.json()
    assert len(data) == 1
    assert data[0]["content"] == "Is the earth flat?"

    # 7. Study: Filter "unresolved"
    # Both attempted, so should be 0
    res = client.get(f"/study/{nb_id}?mode=unresolved")
    assert len(res.json()) == 0

    # Add new question not attempted
    client.post(f"/questions/upload/{nb_id}", json={
        "questions": [{
            "content": "New Q", 
            "type": "true_false", 
            "language": "en", 
            "options": ["T", "F"], 
            "correct_answer": "T", 
            "explanation": "."
        }]
    })
    res = client.get(f"/study/{nb_id}?mode=unresolved")
    assert len(res.json()) == 1
    assert res.json()[0]["content"] == "New Q"

def test_hierarchical_stats(client: TestClient):
    # Tests that stats aggregate from sub-notebooks
    
    # Root: Science (ID 1)
    #   Sub: Physics (ID 2) -> 1 Question (Correct)
    #   Sub: Chemistry (ID 3) -> 1 Question (Incorrect)
    
    r_root = client.post("/notebooks/", json={"name": "Science"}).json()
    r_phy = client.post("/notebooks/", json={"name": "Physics", "parent_id": r_root["id"]}).json()
    r_chem = client.post("/notebooks/", json={"name": "Chemistry", "parent_id": r_root["id"]}).json()
    
    # Upload Q to Physics
    client.post(f"/questions/upload/{r_phy['id']}", json={
        "questions": [{
            "content": "Phy Q", "type": "tf", "language": "en", "options": ["T","F"], "correct_answer": "T", "explanation": "E"
        }]
    })
    # Upload Q to Chemistry
    client.post(f"/questions/upload/{r_chem['id']}", json={
        "questions": [{
            "content": "Chem Q", "type": "tf", "language": "en", "options": ["T","F"], "correct_answer": "T", "explanation": "E"
        }]
    })
    
    # Get IDs
    q_phy = client.get(f"/study/{r_phy['id']}").json()[0]
    q_chem = client.get(f"/study/{r_chem['id']}").json()[0]
    
    # Attempt Phy Correct
    client.post("/attempt/", json={"question_id": q_phy["id"], "selected_option": "T"})
    # Attempt Chem Incorrect
    client.post("/attempt/", json={"question_id": q_chem["id"], "selected_option": "F"})
    
    # Check Stats for ROOT (Science) -> Should aggregate both
    res = client.get(f"/stats/{r_root['id']}")
    stats = res.json()
    assert stats["total_questions"] == 2
    assert stats["attempted"] == 2
    assert stats["correct"] == 1
    assert stats["incorrect"] == 1
    assert stats["accuracy"] == 0.5
