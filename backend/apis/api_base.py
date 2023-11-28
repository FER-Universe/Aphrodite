from fastapi import APIRouter
from apis.version1 import comm_router


api_router = APIRouter()
api_router.include_router(comm_router.router, prefix="/comm", tags=["comm"])
