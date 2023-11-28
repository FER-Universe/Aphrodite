from apis.data.database import SessionLocal, get_db
from apis.data.models import Employee
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/question",
)


# @router.get("/list")
# def question_list():
#     db = SessionLocal()
#     _question_list = db.query(Employee).order_by(Employee.Age.desc()).all()
#     db.close()
#     return _question_list


@router.get("/list")
def question_list():
    with get_db() as db:
        _question_list = db.query(Employee).order_by(Employee.Age.desc()).all()
        return _question_list


@router.get("/simple_question")
async def root():
    return {"message": "Who are you?"}
