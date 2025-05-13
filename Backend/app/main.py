from fastapi import FastAPI, Depends
from app.routes import portfolio
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings, Settings

app = FastAPI(
    title="TradeIQ Financial Analysis API",
    description="Multi-agent system for comprehensive portfolio analysis",
    version="1.0.0"
)

# Include routes
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

origins = [
    "http://localhost:5173",  # Allow localhost
    "http://127.0.0.1:5173",
    "http://localho.st:5173",
    "http://0.0.0.0:5173",    # Allow requests from 0.0.0.0:3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home(settings: Settings = Depends(get_settings)):
    return {
        "message": "Financial AI Agent API",
        "version": "1.0.0",
        "model": settings.llm_model
    }

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

