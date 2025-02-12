from fastapi import FastAPI
from routes import portfolio, stock
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Include routes
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "skr"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

