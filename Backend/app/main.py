from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import auth, users, interviews

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Chatbot API",
    version="1.0.0"
)

# React frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(interviews.router)


@app.get("/")
def root():
    return {
        "message": "AI Interview Chatbot API is running"
    }