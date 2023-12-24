from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apis.data.database import add_message_to_database, query_info_to_database
from apis.data.models import Employee

router = APIRouter(
    prefix="/api/database",
)


@router.get("/add")
def add_db(message: str):
    add_message_to_database(message=message)
    return {"message": "finished to add info to database!"}


@router.get("/query")
def query_db():
    results = query_info_to_database(
        table_name="Employee", filter={"Education": "Masters"}
    )
    return results


@router.get("/simple_query")
async def root():
    return {"message": "Who are you?"}
