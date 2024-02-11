import contextlib
import json
import uuid
from datetime import datetime
from typing import Any, Optional

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound

# Modified by dohee from: from apis.data.models import Dialogue, Employee
from apis.data.models import Dialogue, DialogueUserID, Employee, UserInfo
from configs.config import settings
from schemas.dialogue_sch import DialogueRequestSch, DialogueResponseSch

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_ID}:{settings.DB_PW}@{settings.DB_ADDRESS}/{settings.DB_NAME}"

Base = declarative_base()


def connect_db():
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URL)
    try:
        connection = engine.connect()
    except ConnectionError as e:
        print(f"{e}")
    return connection


def add_message_to_database(message: str, index: int):
    connection = connect_db()
    with Session(connection) as session:
        session.add(
            Dialogue(
                session_id=uuid.uuid4(),
                dialogue=message,
                dialogue_index=index,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        session.commit()


def delete_message_by_session_id(session_id: str = None):
    connection = connect_db()
    with Session(connection) as session:
        session.query(Dialogue).filter(Dialogue.session_id == session_id).delete()
        session.commit()


def delete_message_by_current_time(current_time: datetime = None):
    connection = connect_db()

    with Session(connection) as session:
        session.query(Dialogue).filter(Dialogue.current_time < current_time).delete()
        session.commit()


def query_info_to_database(table_name: str, filter: Optional[dict] = None):
    connection = connect_db()
    with Session(connection) as session:
        try:
            if filter is None:
                results = session.query(Employee).limit(10).all()
            else:
                if list(filter.keys())[0] == "Age":
                    filter = Employee.Age == filter["Age"]
                elif list(filter.keys())[0] == "City":
                    filter = Employee.City == filter["City"]
                elif list(filter.keys())[0] == "PaymentTier":
                    filter = Employee.PaymentTier == filter["PaymentTier"]
                elif list(filter.keys())[0] == "Gender":
                    filter = Employee.Gender == filter["Gender"]
                elif list(filter.keys())[0] == "ExperienceInCurrentDomain":
                    filter = (
                        Employee.ExperienceInCurrentDomain
                        == filter["ExperienceInCurrentDomain"]
                    )

                results = (
                    session.query(Employee)
                    .filter(filter)
                    .order_by(Employee.JoiningYear)
                    .all()
                )
        except NoResultFound as e:
            print(e)
    return results


def add_message_to_database_with_user_id(req: DialogueRequestSch):
    connection = connect_db()
    with Session(connection) as session:
        session.add(
            DialogueUserID(
                user_id=req.user_id,
                session_id=uuid.uuid4(),
                dialogue=req.message,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        session.commit()


def add_user_info(user_id: int, name: str, age: int, career: str = "Empty"):
    connection = connect_db()
    with Session(connection) as session:
        session.add(UserInfo(user_id=user_id, name=name, age=age, career=career))
        session.commit()


def find_user_id(user_id: int, mode: int, message: str = None):
    connection = connect_db()
    if mode == 1:
        with Session(connection) as session:
            try:
                result = (
                    session.query(UserInfo.name, DialogueUserID.dialogue)
                    .join(DialogueUserID)
                    .filter(UserInfo.user_id == user_id)
                    .order_by(DialogueUserID.current_time.desc())
                    .first()
                )
            except TypeError:
                result = None

        message = (
            f"user_name: {result[0]}, current message: {result[1]}"
            if result
            else "User information corresponding to that user ID could not be found."
        )
        return message
