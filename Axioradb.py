from passlib.hash import bcrypt
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import (
    PrimaryKeyConstraint, create_engine, ForeignKey,
    Column, String, Integer, CHAR, SmallInteger,
    Text, DateTime
)
from sqlalchemy.orm import relationship, declarative_base

engine = create_engine("sqlite:///axioradb.db")
Base = declarative_base()

class users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    email = Column(String)
    sessions = relationship("Session", back_populates="user")

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
    __tablename__ = 'llm' 
    llm_id = Column(Integer, primary_key=True, autoincrement=True) 
    llm_name = Column(String(255), nullable=False)
    parameters = Column(SmallInteger)
    install_llm_code = Column(String)
    
    # Relationships
    sessions = relationship("Session", back_populates="llm")
    chats = relationship("Chat", back_populates="llm")
    session_memories = relationship("SessionMemory", back_populates="llm")

    def __init__(self, llm_name, install_llm_code, parameters=None):
        self.llm_name = llm_name
        self.parameters = parameters
        self.install_llm_code = install_llm_code

    def __repr__(self):
        return f"<LLM(llm_id={self.llm_id}, llm_name='{self.llm_name}', parameters={self.parameters}, install_llm_code='{self.install_llm_code}')>"
    
class Session(Base):
    __tablename__ = "session"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    data_info = Column(Text) 
    llm_id = Column(Integer, ForeignKey("llm.llm_id", ondelete="CASCADE"), nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("users", back_populates="sessions")
    llm = relationship("LLM", back_populates="sessions")
    data_sets = relationship("DataSet", back_populates="session")
    final_reports = relationship("FinalReport", back_populates="session")
    chats = relationship("Chat", back_populates="session")
    summaries = relationship("Summary", back_populates="session")
    session_memories = relationship("SessionMemory", back_populates="session")

    def __init__(self, user_id, llm_id, data_info=None):
        self.user_id = user_id
        self.llm_id = llm_id
        self.data_info = data_info

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user_id}, llm_id={self.llm_id}, creation_date={self.creation_date})>"

class DataSet(Base):
    __tablename__ = "data_set"  
    data_set_id = Column(Integer, primary_key=True, autoincrement=True)  
    session_id = Column(Integer, ForeignKey('session.session_id', ondelete='CASCADE'), nullable=False)  
    raw_data = Column(Text)  
    transformed_data_set = Column(Text)  
    uploaded_at = Column(DateTime, default=datetime.utcnow) 
    
    # Relationships
    session = relationship("Session", back_populates="data_sets")
    dashboards = relationship("Dashboard", back_populates="data_set")

    def __init__(self, session_id, raw_data=None, transformed_data_set=None):
        self.session_id = session_id
        self.raw_data = raw_data
        self.transformed_data_set = transformed_data_set

    def __repr__(self):
        return f"<DataSet(data_set_id={self.data_set_id}, session_id={self.session_id}, raw_data='{self.raw_data}')>"

class Dashboard(Base):
    __tablename__ = "dashboards"  
    dashboard_id = Column(Integer, primary_key=True, autoincrement=True)  
    data_set_id = Column(Integer, ForeignKey('data_set.data_set_id', ondelete='CASCADE'), nullable=False)  

    # Relationships
    data_set = relationship("DataSet", back_populates="dashboards")
    charts = relationship("Chart", back_populates="dashboard")
    final_reports = relationship("FinalReport", back_populates="dashboard")

    def __init__(self, data_set_id):
        self.data_set_id = data_set_id

    def __repr__(self):                      
        return f"<Dashboard(dashboard_id={self.dashboard_id}, data_set_id={self.data_set_id})>"           
    
class FinalReport(Base):
    __tablename__ = "final_report"  
    report_id = Column(Integer, primary_key=True, autoincrement=True)  
    session_id = Column(Integer, ForeignKey('session.session_id', ondelete='CASCADE'), nullable=False)  
    recommendation = Column(Text, nullable=False)  
    dashboard_id = Column(Integer, ForeignKey('dashboards.dashboard_id', ondelete='CASCADE'), nullable=False) 

    # Relationships
    session = relationship("Session", back_populates="final_reports")
    dashboard = relationship("Dashboard", back_populates="final_reports")

    def __init__(self, session_id, recommendation, dashboard_id):
        self.session_id = session_id
        self.recommendation = recommendation
        self.dashboard_id = dashboard_id

    def __repr__(self):
        return f"<FinalReport(report_id={self.report_id}, session_id={self.session_id}, recommendation='{self.recommendation}')>"

class Chat(Base):
    __tablename__ = "chat"  
    chat_id = Column(Integer, primary_key=True, autoincrement=True) 
    session_id = Column(Integer, ForeignKey('session.session_id', ondelete='CASCADE'), nullable=False)  
    llm_id = Column(Integer, ForeignKey('llm.llm_id', ondelete='CASCADE'), nullable=False)  
    number_dataset = Column(Integer, nullable=False) 

    # Relationships
    session = relationship("Session", back_populates="chats")
    llm = relationship("LLM", back_populates="chats")
    chat_histories = relationship("ChatHistory", back_populates="chat")

    def __init__(self, session_id, llm_id, number_dataset):
        self.session_id = session_id
        self.llm_id = llm_id
        self.number_dataset = number_dataset

    def __repr__(self):
        return f"<Chat(chat_id={self.chat_id}, session_id={self.session_id}, llm_id={self.llm_id})>"

class ChatHistory(Base):
    __tablename__ = "chat_history"  
    chat_history_id = Column(Integer, primary_key=True, autoincrement=True)  
    chat_id = Column(Integer, ForeignKey('chat.chat_id', ondelete='CASCADE'), nullable=False)  
    message_number = Column(Integer, nullable=False)
    prompt = Column(Text)   
    response = Column(Text)  
    additional_kwargs = Column(Text) 
    response_metadata = Column(Text)  

    # Relationships
    chat = relationship("Chat", back_populates="chat_histories")
    chat_datasets = relationship("ChatDataSet", back_populates="chat_history")
    questions = relationship("Question", back_populates="chat_history")
    session_memories = relationship("SessionMemory", back_populates="chat_history")

    def __init__(self, chat_id, message_number, prompt=None, response=None):
        self.chat_id = chat_id
        self.message_number = message_number
        self.prompt = prompt
        self.response = response

    def __repr__(self):
        return f"<ChatHistory(chat_history_id={self.chat_history_id}, message_number={self.message_number}, prompt='{self.prompt}')>"

class ChatDataSet(Base):
    __tablename__ = "chat_dataset"  
    chat_dataset_id = Column(Integer, primary_key=True, autoincrement=True) 
    chat_history_id = Column(Integer, ForeignKey('chat_history.chat_history_id', ondelete='CASCADE'), nullable=False)  

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="chat_datasets")

    def __init__(self, chat_history_id):
        self.chat_history_id = chat_history_id

    def __repr__(self):
        return f"<ChatDataSet(chat_dataset_id={self.chat_dataset_id}, chat_history_id={self.chat_history_id})>"

class Question(Base):
    __tablename__ = "questions"  
    chat_history_id = Column(Integer, ForeignKey('chat_history.chat_history_id', ondelete='CASCADE'), nullable=False) 
    question_num = Column(Integer, nullable=False)  
    question = Column(Text, nullable=False) 

    __table_args__ = (
        PrimaryKeyConstraint('chat_history_id', 'question_num'),
    )

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="questions")

    def __init__(self, chat_history_id, question_num, question):
        self.chat_history_id = chat_history_id
        self.question_num = question_num
        self.question = question

    def __repr__(self):
        return f"<Question(chat_history_id={self.chat_history_id}, question_num={self.question_num})>"

class Summary(Base):
    __tablename__ = "summary" 
    summary_id = Column(Integer, primary_key=True, autoincrement=True)  
    summary_content = Column(Text)  
    session_id = Column(Integer, ForeignKey('session.session_id', ondelete='CASCADE'), nullable=False)  

    # Relationships
    session = relationship("Session", back_populates="summaries")

    def __init__(self, session_id, summary_content=None):
        self.session_id = session_id
        self.summary_content = summary_content

    def __repr__(self):
        return f"<Summary(summary_id={self.summary_id}, session_id={self.session_id})>"

class Chart(Base):
    __tablename__ = "charts"  
    chart_id = Column(Integer, primary_key=True, autoincrement=True)  
    chart_type = Column(String(255), nullable=False)  
    dashboard_id = Column(Integer, ForeignKey('dashboards.dashboard_id', ondelete='CASCADE'), nullable=False)  

    # Relationships
    dashboard = relationship("Dashboard", back_populates="charts")

    def __init__(self, chart_type, dashboard_id):
        self.chart_type = chart_type
        self.dashboard_id = dashboard_id

    def __repr__(self):
        return f"<Chart(chart_id={self.chart_id}, chart_type='{self.chart_type}')>"

class SessionMemory(Base):
    __tablename__ = "session_memory"  
    session_id = Column(Integer, ForeignKey('session.session_id', ondelete='CASCADE'), primary_key=True) 
    llm_id = Column(Integer, ForeignKey('llm.llm_id', ondelete='CASCADE'), primary_key=True)  
    chat_history_id = Column(Integer, ForeignKey('chat_history.chat_history_id', ondelete='CASCADE'), nullable=False)  
    message_number = Column(Integer, nullable=False)  
    prompt = Column(Text)  
    response = Column(Text)  
    additional_kwargs = Column(Text)  
    response_metadata = Column(Text)  

    # Relationships
    session = relationship("Session", back_populates="session_memories")
    llm = relationship("LLM", back_populates="session_memories")
    chat_history = relationship("ChatHistory", back_populates="session_memories")

    def __init__(self, session_id, llm_id, chat_history_id, message_number):
        self.session_id = session_id
        self.llm_id = llm_id
        self.chat_history_id = chat_history_id
        self.message_number = message_number

    def __repr__(self):
        return f"<SessionMemory(session_id={self.session_id}, llm_id={self.llm_id}, message_number={self.message_number})>"

Base.metadata.create_all(engine)
