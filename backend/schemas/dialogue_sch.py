from pydantic import BaseModel


class DialogueRequestSch(BaseModel):
    message: str
    user_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "message": "Hello, world",
                "user_id": 1234,
            }
        }
