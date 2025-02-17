from fastapi import FastAPI, Depends
from routes import portfolio, stock
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Include routes
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])

origins = [
    "http://localho.st:5173",  # Allow localhost
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
async def home():
    return {"message": "good so far"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)


# from app.utils.config import Settings, get_settings

# def some_endpoint(settings: Settings = Depends(get_settings)):
#     return {"message": "Using Crisp Identifier", "identifier": settings.crisp_identifier}