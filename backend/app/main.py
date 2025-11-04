from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.tickets import router as tickets_router
from app.database import engine
from app.models import Base

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(tickets_router)

@app.get("/health")
def health():
    return {"status": "ok"}

