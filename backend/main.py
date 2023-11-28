from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apis.version1 import question_router
from apis.version1 import openai_router

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


app.include_router(question_router.router)
app.include_router(openai_router.router)

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
