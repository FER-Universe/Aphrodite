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

# Modified by dohee from: from apis.data.models import DialogueSession, Employee
from apis.data.models import (
    DialogueSession,
    Employee,
    DialogueSession_with_userid,
    UserInfo,
)
from configs.config import settings

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_ID}:{settings.DB_PW}@{settings.DB_ADDRESS}/{settings.DB_NAME}"

Base = declarative_base()


def connect_db():
    engine = sqlalchemy.create_engine(
        SQLALCHEMY_DATABASE_URL,
        json_serializer=lambda x: json.dumps(
            x, ensure_ascii=False, default=str
        ),  # 옵션, 없어도 됨
    )
    try:
        connection = engine.connect()
    except ConnectionError as e:
        print(f"{e}")
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


def delete_message_by_session_id(session_id: str = None):
    connection = connect_db()
    with Session(connection) as session:
        session.query(DialogueSession).filter(
            DialogueSession.session_id == session_id
        ).delete()
        session.commit()


def delete_message_by_current_time(current_time: datetime = None):
    connection = connect_db()

    with Session(connection) as session:
        session.query(DialogueSession).filter(
            DialogueSession.current_time < current_time
        ).delete()
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


# Add by dohee
def add_message_to_database_with_userid(message: str, user_id: int):
    connection = connect_db()
    with Session(connection) as session:
        session.add(
            DialogueSession_with_userid(
                user_id=user_id,
                session_id=uuid.uuid4(),
                dialogue=message,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        session.commit()


def add_user_info(user_id: int, name: str, age: int, career: str = "Empty"):
    connection = connect_db()
    with Session(connection) as session:
        session.add(UserInfo(user_id=user_id, name=name, age=age, career=career))
        session.commit()


def manipulate_with_user_id(user_id: int, mode: int, message: str = None):
    connection = connect_db()
    if mode == 1:
        with Session(connection) as session:
            # 해당 user의 가장 최근 메세지 조회
            try:
                print(
                    session.query(UserInfo.name, DialogueSession_with_userid.dialogue)
                    .join(  # UserInfo에서 이름을, DialogSession에서 dialog를 쿼리함
                        DialogueSession_with_userid
                    )
                    .filter(UserInfo.user_id == user_id)
                )
                result = (
                    session.query(
                        UserInfo.name, DialogueSession_with_userid.dialogue
                    )  # UserInfo에서 이름을, DialogSession에서 dialog를 쿼리함
                    .join(
                        DialogueSession_with_userid
                    )  # DialogSession을 기준으로 Userinfo의 이름, 메세지, 그리고 userid 정보가 들어간 새로운 테이블 생성
                    .filter(
                        UserInfo.user_id == user_id
                    )  # 테이블 생성 시, user_id가 전달된 인자와 동일한 경우들만 추출
                    .order_by(
                        DialogueSession_with_userid.current_time.desc()
                    )  # 메세지 생성 시간을 기준으로 내림차순
                    .first()  # 가장 첫 번째 메세지(가장 최근 메세지) 도출
                )
            except TypeError:
                result = None

        message = (
            f"user_name: {result[0]}, current message: {result[1]}"
            if result
            else "해당 user id에 해당하는 사용자 정보를 찾을 수 없습니다."
        )
        return message
