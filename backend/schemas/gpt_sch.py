from pydantic import BaseModel


class GptRequestSch(BaseModel):
    title_nm: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title_nm": "Base Tesla Model 3 Inventory has $2,410 discount and now Qualifies for $7,500 Tax Credit"
            }
        }


class GptResponseSch(BaseModel):
    openai_msg_ctt: str
    emotion_va: str
    emotion_dis: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "openai_msg_ctt": "openai 메시지 내용 입니다",
                "emotion": "default 감정 상태 입니다",
                "emotion_dis": "이산 감정 클래스에 기반한 감정 상태 입니다.",
            }
        }


class GptResponseSch_msgonly(BaseModel):
    openai_msg_ctt: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "openai_msg_ctt": "openai 메시지 내용 입니다",
            }
        }
