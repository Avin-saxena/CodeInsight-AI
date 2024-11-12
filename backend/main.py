from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyzer, gpt, mermaid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyzer.router)
app.include_router(gpt.router)
app.include_router(mermaid.router)