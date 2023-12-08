from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()


class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)


class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    create_date = Column(DateTime, nullable=False)
    question_id = Column(Integer, ForeignKey("question.id"))
    question = relationship("Question", backref="answers")


class Employee(Base):
    __tablename__ = "employee"

    # id = Column(Integer, primary_key=True)
    Age = Column(Integer, primary_key=True)
    Education = Column(CHAR)
    JoiningYear = Column(Integer)
    City = Column(CHAR)
    PaymentTier = Column(Integer)
    Gender = Column(CHAR)
    EverBenched = Column(CHAR)
    ExperienceInCurrentDomain = Column(Integer)
    LeaveOrNot = Column(Integer)
