import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apis.version1 import database_router, emotion_router, openai_router

app = FastAPI()

origins = [
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
def hello():
    return {"message": "Hello, everyone! :)"}


app.include_router(openai_router.router)
app.include_router(emotion_router.router)
app.include_router(database_router.router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
