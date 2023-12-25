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

from apis.data.models import DialogueSession, Employee
from configs.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_ID}:{settings.DB_PW}@{settings.DB_ADDRESS}/{settings.DB_NAME}"

Base = declarative_base()


def connect_db():
    engine = sqlalchemy.create_engine(
        SQLALCHEMY_DATABASE_URL,
        json_serializer=lambda x: json.dumps(x, ensure_ascii=False, default=str),
    )
    connection = engine.connect()
    return connection


def add_message_to_database(message: str):
    connection = connect_db()
    with Session(connection) as session:
        session.add(
            DialogueSession(
                session_id=uuid.uuid4(),
                dialogue=message,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
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
