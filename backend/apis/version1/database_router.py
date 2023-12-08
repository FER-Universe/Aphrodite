from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apis.data.database import query_db
from apis.data.models import Employee

router = APIRouter(
    prefix="/api/database",
)


@router.get("/query")
def query_to_database():
    results = query_db(table_name="Employee", filter={"Education": "Masters"})
    return results


@router.get("/simple_query")
async def root():
    return {"message": "Who are you?"}
