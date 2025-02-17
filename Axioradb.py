from passlib.hash import bcrypt
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import(
    create_engine, ForeignKey,
    Column, String, Integer, CHAR, SmallInteger,
    Text, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine("sqlite:///axioradb.db")
Base = declarative_base()

class users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password) 

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"
    
class LLM(Base):
    __tablename__ = 'LLM' 

    # Columns
    llm_id = Column(Integer, primary_key=True, autoincrement=True) 
    llm_name = Column(String(255), nullable=False)
    parameters = Column(SmallInteger)
    install_llm_code = Column(String)

    def __init__(self, llm_name, install_llm_code, parameters=None):
        self.llm_name = llm_name
        self.parameters = parameters
        self.install_llm_code = install_llm_code

    def __repr__(self):
        return f"<LLM(llm_id={self.llm_id}, llm_name='{self.llm_name}', parameters={self.parameters},install_llm_code='{self.install_llm_code}')>"
    
class Session(Base):
    __tablename__ = "Session"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    data_info = Column(Text) 
    llm_id = Column(Integer, ForeignKey("LLM.llm_id", ondelete="CASCADE"), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    llm = relationship("LLM", back_populates="sessions")

    def __init__(self, user_id, llm_id, data_info=None):
        self.user_id = user_id
        self.llm_id = llm_id
        self.data_info = data_info

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user_id}, llm_id={self.llm_id}, creation_date={self.creation_date})>"

class DataSet(Base):
    __tablename__ = "data_set"  # Table name in SQLite

    # Define columns
    data_set_id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    session_id = Column(Integer, ForeignKey('session.session_id', ondelete='CASCADE'), nullable=False)  # Foreign key
    raw_data = Column(Text)  # Raw data stored as text
    transformed_data_set = Column(Text)  # Transformed data stored as text
    uploaded_at = Column(DateTime, default=datetime.utcnow)  # Timestamp with default value
    # Define relationship to the Session table
    session = relationship("Session", back_populates="data_sets")

    def __init__(self, session_id, raw_data=None, transformed_data_set=None):
        
        self.session_id = session_id
        self.raw_data = raw_data
        self.transformed_data_set = transformed_data_set

    def __repr__(self):
        
        return f"<DataSet(data_set_id={self.data_set_id}, session_id={self.session_id}, uploaded_at='{self.uploaded_at}')>"





Base.metadata.create_all(engine)