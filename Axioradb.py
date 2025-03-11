from passlib.hash import bcrypt
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import (
    PrimaryKeyConstraint, create_engine, ForeignKey,
    Column, String, Integer, CHAR, SmallInteger,
    Text, DateTime
)
from sqlalchemy import func
from sqlalchemy.orm import relationship, declarative_base

engine = create_engine("sqlite:///axioradb.db")
Base = declarative_base()

class User(Base):
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

# 2. LLM Table
class LLM(Base):
    __tablename__ = "llm"
    llm_id = Column(Integer, primary_key=True, autoincrement=True)
    llm_name = Column(String(255), nullable=False)
    parameters = Column(SmallInteger)
    install_llm_code = Column(String)
    
    # Relationships
    sessions = relationship("Session", back_populates="llm")
    session_memories = relationship("SessionMemory", back_populates="llm")

    def __init__(self, llm_name, parameters=None, install_llm_code=None):
        self.llm_name = llm_name
        self.parameters = parameters
        self.install_llm_code = install_llm_code

    def __repr__(self):
        return f"<LLM(llm_id={self.llm_id}, llm_name='{self.llm_name}')>"


# 3. Dataset Table
class Dataset(Base):
    __tablename__ = "dataset"
    dataset_id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=func.now())
    data_info = Column(Text)
    data_summary = Column(Text)
    data_sample = Column(Text)
    data_columns = Column(Text)
    
    # Relationships
    sessions = relationship("Session", back_populates="dataset")
    clean_datasets = relationship("CleanDataset", back_populates="original_dataset")

    def __init__(self, dataset_name, raw_data, data_info=None, data_summary=None, data_sample=None, data_columns=None):
        self.dataset_name = dataset_name
        self.raw_data = raw_data
        self.data_info = data_info
        self.data_summary = data_summary
        self.data_sample = data_sample
        self.data_columns = data_columns

    def __repr__(self):
        return f"<Dataset(dataset_id={self.dataset_id}, dataset_name='{self.dataset_name}')>"


# 4. CleanDataset Table
class CleanDataset(Base):
    __tablename__ = "cleanDataset"
    clean_dataset_id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=False)
    original_dataset_id = Column(Integer, ForeignKey("dataset.dataset_id"))
    cleaned_at = Column(DateTime, default=func.now())
    data_info = Column(Text)
    data_summary = Column(Text)
    data_sample = Column(Text)
    data_columns = Column(Text)
    
    # Relationships
    original_dataset = relationship("Dataset", back_populates="clean_datasets")
    sessions = relationship("Session", back_populates="clean_dataset")

    def __init__(self, dataset_name, raw_data, original_dataset_id, data_info=None, data_summary=None, data_sample=None, data_columns=None):
        self.dataset_name = dataset_name
        self.raw_data = raw_data
        self.original_dataset_id = original_dataset_id
        self.data_info = data_info
        self.data_summary = data_summary
        self.data_sample = data_sample
        self.data_columns = data_columns

    def __repr__(self):
        return f"<CleanDataset(clean_dataset_id={self.clean_dataset_id}, dataset_name='{self.dataset_name}')>"


# 5. Session Table
class Session(Base):
    __tablename__ = "session"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    llm_id = Column(Integer, ForeignKey("llm.llm_id"))
    dataset_id = Column(Integer, ForeignKey("dataset.dataset_id"))
    clean_dataset_id = Column(Integer, ForeignKey("cleanDataset.clean_dataset_id"))
    creation_date = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    llm = relationship("LLM", back_populates="sessions")
    dataset = relationship("Dataset", back_populates="sessions")
    clean_dataset = relationship("CleanDataset", back_populates="sessions")
    session_memories = relationship("SessionMemory", back_populates="session", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="session", uselist=False, cascade="all, delete-orphan")
    questions = relationship("Questions", back_populates="session", cascade="all, delete-orphan")
    dashboards = relationship("Dashboards", back_populates="session", cascade="all, delete-orphan")
    final_reports = relationship("FinalReport", back_populates="session", cascade="all, delete-orphan")

    def __init__(self, user_id, llm_id, dataset_id, clean_dataset_id=None):
        self.user_id = user_id
        self.llm_id = llm_id
        self.dataset_id = dataset_id
        self.clean_dataset_id = clean_dataset_id

    def __repr__(self):
        return f"<Session(session_id={self.session_id}, user_id={self.user_id})>"


# 6. SessionMemory Table
class SessionMemory(Base):
    __tablename__ = "session_memory"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("session.session_id", ondelete="CASCADE"))
    llm_id = Column(Integer, ForeignKey("llm.llm_id"))
    message_date = Column(DateTime, default=func.now(),nullable=False)
    prompt = Column(Text)
    response = Column(Text)
    additional_kwargs = Column(Text)
    response_metadata = Column(Text)
    chat = Column(Text)
    
    # Relationships
    session = relationship("Session", back_populates="session_memories")
    llm = relationship("LLM", back_populates="session_memories")

    def __init__(self, session_id, llm_id, message_date, prompt=None, response=None, additional_kwargs=None, response_metadata=None, chat=False):
        self.session_id = session_id
        self.llm_id = llm_id
        self.message_date = message_date
        self.prompt = prompt
        self.response = response
        self.additional_kwargs = additional_kwargs
        self.response_metadata = response_metadata
        self.chat = chat

    def __repr__(self):
        return f"<SessionMemory(message_id={self.message_id}, session_id={self.session_id})>"


# 7. Summary Table
class Summary(Base):
    __tablename__ = "summary"
    session_id = Column(Integer, ForeignKey("session.session_id", ondelete="CASCADE"), primary_key=True)
    summary_content = Column(Text)
    
    # Relationship
    session = relationship("Session", back_populates="summary")

    def __init__(self, session_id, summary_content=None):
        self.session_id = session_id
        self.summary_content = summary_content

    def __repr__(self):
        return f"<Summary(session_id={self.session_id})>"


# 8. Questions Table
class Questions(Base):
    __tablename__ = "questions"
    question_num = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("session.session_id", ondelete="CASCADE"), primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    
    # Relationship
    session = relationship("Session", back_populates="questions")

    def __init__(self, question_num, session_id, question, answer=None):
        self.question_num = question_num
        self.session_id = session_id
        self.question = question
        self.answer = answer

    def __repr__(self):
        return f"<Questions(question_num={self.question_num}, session_id={self.session_id})>"


# 9. Dashboards Table
class Dashboards(Base):
    __tablename__ = "dashboards"
    dashboard_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("session.session_id", ondelete="CASCADE"))
    
    # Relationships
    session = relationship("Session", back_populates="dashboards")
    charts = relationship("Charts", back_populates="dashboard", cascade="all, delete-orphan")
    final_reports = relationship("FinalReport", back_populates="dashboard", cascade="all, delete-orphan")

    def __init__(self, session_id):
        self.session_id = session_id

    def __repr__(self):
        return f"<Dashboards(dashboard_id={self.dashboard_id}, session_id={self.session_id})>"


# 10. Charts Table
class Charts(Base):
    __tablename__ = "charts"
    chart_id = Column(Integer, primary_key=True, autoincrement=True)
    chart_type = Column(String(255), nullable=False)
    dashboard_id = Column(Integer, ForeignKey("dashboards.dashboard_id", ondelete="CASCADE"))
    chart_style = Column(Text)
    chart_code = Column(Text)
    
    # Relationships
    dashboard = relationship("Dashboards", back_populates="charts")
    columns = relationship("Columns", back_populates="chart", cascade="all, delete-orphan")

    def __init__(self, chart_type, dashboard_id, chart_style=None, chart_code=None):
        self.chart_type = chart_type
        self.dashboard_id = dashboard_id
        self.chart_style = chart_style
        self.chart_code = chart_code

    def __repr__(self):
        return f"<Charts(chart_id={self.chart_id}, chart_type='{self.chart_type}')>"


# 11. Columns Table
class Columns(Base):
    __tablename__ = "columns"
    column_id = Column(Integer, primary_key=True, autoincrement=True)
    chart_id = Column(Integer, ForeignKey("charts.chart_id", ondelete="CASCADE"))
    column_name = Column(Text)
    
    # Relationship
    chart = relationship("Charts", back_populates="columns")

    def __init__(self, chart_id, column_name):
        self.chart_id = chart_id
        self.column_name = column_name

    def __repr__(self):
        return f"<Columns(column_id={self.column_id}, chart_id={self.chart_id})>"


# 12. FinalReport Table
class FinalReport(Base):
    __tablename__ = "final_report"
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("session.session_id", ondelete="CASCADE"), nullable=False)
    recommendation = Column(Text, nullable=False)
    dashboard_id = Column(Integer, ForeignKey("dashboards.dashboard_id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="final_reports")
    dashboard = relationship("Dashboards", back_populates="final_reports")

    def __init__(self, session_id, recommendation, dashboard_id):
        self.session_id = session_id
        self.recommendation = recommendation
        self.dashboard_id = dashboard_id

    def __repr__(self):
        return f"<FinalReport(report_id={self.report_id}, session_id={self.session_id})>"   
Base.metadata.create_all(engine)