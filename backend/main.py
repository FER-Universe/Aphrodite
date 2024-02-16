import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apis.version1 import (
    clip_matching_router,
    database_router,
    openai_router,
    stt_router,
    emotion_router,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(database_router.router)
app.include_router(openai_router.router)
app.include_router(stt_router.router)
app.include_router(clip_matching_router.router)
app.include_router(emotion_router.router)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["app/files/"],
    )
