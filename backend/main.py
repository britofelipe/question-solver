from fastapi import FastAPI
from app.core.database import init_db
from app.routers import notebooks, questions, stats

app = FastAPI(title="Question Solver API")

# Include Routers
app.include_router(notebooks.router)
app.include_router(questions.router)
app.include_router(stats.router)

@app.get("/")
def read_root():
    return {"message": "Question Solver API is running"}

@app.on_event("startup")
def on_startup():
    init_db()
