from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apis.data.database import (
    add_message_to_database,
    add_message_to_database_with_user_id,
    add_user_info,
    delete_message_by_current_time,
    delete_message_by_session_id,
    find_user_id,
    query_info_to_database,
)
from apis.data.models import Employee
from schemas.dialogue_sch import DialogueRequestSch, DialogueResponseSch

router = APIRouter(
    prefix="/api/database",
)


@router.get("/simple_query")
def simple_query():
    return {"message": "Who are you?"}


@router.get("/add")
def add_db(message: str, index: int):
    add_message_to_database(message=message, index=index)
    return {"message": "finished to add info to database!"}


@router.get("/query")
def query_db():
    results = query_info_to_database(
        table_name="Employee", filter={"Education": "Masters"}
    )
    return results


@router.get(
    "/find_user_id",
    description="search current message",
)
def find_user_id(user_id: int, mode: int, message: str = None):
    message = find_user_id(user_id=user_id, mode=mode, message=message)
    return message


@router.post("/add_message_with_user_id")
def add_message_with_user_id(req: DialogueRequestSch):
    add_message_to_database_with_user_id(req)
    return {"message": "finished to add info to database!"}


@router.post(
    "/add_user_info", description="add info ordered by: user_id, name, age, career"
)
def add_user_info(user_id: int, name: str, age: int, career: str):
    add_user_info(user_id=user_id, name=name, age=age, career=career)
    return {"message": "finished to add info to database!"}


@router.delete("/delete_by_current_time", description="format: YYYY-MM-DD hh:mm:ss")
def delete_by_current_time(current_time: Optional[str]):
    current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    delete_message_by_current_time(current_time=current_time)
    return {"message": "finished to delete message from database!"}


@router.delete("/delete_by_session_id")
def delete_by_session_id(session_id: str):
    delete_message_by_session_id(session_id=session_id)
    return {"message": "finished to delete message from database!"}
