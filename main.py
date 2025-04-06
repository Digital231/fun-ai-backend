from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import ai_routes

app = FastAPI(title="PersonaChat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ai-fun-chat.netlify.app"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_routes.router, prefix="/api", tags=["tests"])

@app.get("/")
def read_root():
    return {"message": "Welcome to PersonaChat API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)