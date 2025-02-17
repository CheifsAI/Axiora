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

engine = create_engine("sqlite:///axiora.db")
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

    def __init__(self, llm_name, parameters=None):
        self.llm_name = llm_name
        self.parameters = parameters

    def __repr__(self):
        return f"<LLM(llm_id={self.llm_id}, llm_name='{self.llm_name}', parameters={self.parameters})>"
    
class Session(Base):
    __tablename__ = "Session"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    data_info = Column(Text)  # TEXT (can be NULL)
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






Base.metadata.create_all(engine)