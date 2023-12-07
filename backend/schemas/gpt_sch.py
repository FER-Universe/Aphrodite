# demo=fast-api > schemas > gpt_sch.py 파일 생성
from pydantic import BaseModel


# 요청시
class GptRequestSch(BaseModel):
    title_nm: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title_nm": "Base Tesla Model 3 Inventory has $2,410 discount and now Qualifies for $7,500 Tax Credit"
            }
        }


# 결과를 응답하는 경우
class GptResponseSch(BaseModel):
    openai_msg_ctt: str
    emotion: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "openai_msg_ctt": "openai 메시지 내용 입니다",
                "emotion": "default 감정 상태 입니다",
            }
        }


# 결과를 응답하는 경우
class GptResponseSch_msgonly(BaseModel):
    openai_msg_ctt: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "openai_msg_ctt": "openai 메시지 내용 입니다",
            }
        }
