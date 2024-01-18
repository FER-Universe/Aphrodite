from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from datetime import datetime  # add by dohee
from typing import Optional

from apis.data.database import (
    add_message_to_database,
    query_info_to_database,
    delete_message_by_current_time,
    delete_message_by_session_id,
    # Add by dohee kang
    add_message_to_database_with_userid,
    add_user_info,
    manipulate_with_user_id,
)
from apis.data.models import Employee

router = APIRouter(
    prefix="/api/database",
)


@router.get("/add")
def add_db(message: str):
    add_message_to_database(message=message)
    return {"message": "finished to add info to database!"}


@router.get("/delete_by_current_time", description="time format: YYYY-MM-DD hh:mm:ss")
def delete_by_cur_time(current_time: Optional[str]):
    current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    delete_message_by_current_time(current_time=current_time)
    return {"message": "finished to delete message from database!"}


@router.get("/delete_by_session_id")
def delete_by_cur_time(session_id: str):
    delete_message_by_session_id(session_id=session_id)
    return {"message": "finished to delete message from database!"}


@router.get("/query")
def query_db():
    results = query_info_to_database(
        table_name="Employee", filter={"Education": "Masters"}
    )
    return results


@router.get("/simple_query")
async def root():
    return {"message": "Who are you?"}


# Add by dohee
@router.get("/add_message_with_userid")
def add_db(message: str, user_id: int):
    add_message_to_database_with_userid(message=message, user_id=user_id)
    return {"message": "finished to add info to database!"}


@router.get(
    "/add_userinfo", description="add info ordered by: user_id, name, age, career"
)
def add_db(user_id: int, name: str, age: int, career: str):
    add_user_info(user_id=user_id, name=name, age=age, career=career)
    return {"message": "finished to add info to database!"}


@router.get(
    "/manipulate_with_user_id",
    description="mode; 1: search current message 2. delete current message 3. modify current message",
)
def add_db(user_id: int, mode: int, message: str = None):
    message = manipulate_with_user_id(user_id=user_id, mode=mode, message=message)
    return message
