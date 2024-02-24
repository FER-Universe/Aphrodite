"""reference link: 
https://github.com/grpc/grpc/blob/master/examples/python/helloworld/async_greeter_client.py
"""

import asyncio
import logging

import grpc
import hello_pb2
import hello_pb2_grpc
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()


async def hello_bot(connection_string: str, name: str):
    async with grpc.aio.insecure_channel(connection_string) as channel:
        stub = hello_pb2_grpc.StreamHelloStub(channel)

        async for response in stub.GetResponse(hello_pb2.HelloRequest(name=name)):
            logger.info("HelloBot client received message with " + response.message)


@router.post("/hello_by_grpc")
async def root(port: int, name: str):
    await hello_bot(connection_string=f"localhost:{port}", name=name)
    return {"message": "hello world"}
