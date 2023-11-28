from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CHAR
from sqlalchemy.orm import relationship

from apis.data.database import Base


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
