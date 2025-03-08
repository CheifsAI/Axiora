from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

class DatabaseManager:
    def __init__(self, DATABASE_URL = "sqlite:///axioradb.db"):
        self.engine = create_engine(DATABASE_URL)
        self.Base = automap_base()
        self.Base.prepare(autoload_with=self.engine)
        self.session = Session(self.engine)

    def saveDataSet(self,path,name,info,summary,sample,cols):
        dataSet = self.Base.classes.dataset
        newDataSet = dataSet(raw_data=path,
                             dataset_name = name,
                             data_info=info,
                             data_summary=summary,
                             data_sample=sample,
                             data_columns=cols)
        self.session.add(newDataSet)
        self.session.flush()
        dataset_id = newDataSet.dataset_id
        self.session.commit()
        return dataset_id

    def saveSession(self,user,llm,dataset):
        sessionTable = self.Base.classes.session
        newSession = sessionTable(user_id=user,llm_id=llm,dataset_id=dataset)
        self.session.add(newSession)
        self.session.flush()
        session_id = newSession.session_id  
        self.session.commit()
        return session_id
    
    def saveSummary(self,session,summary_content):
        summary = self.Base.classes.summary
        newSummary = summary(session_id=session,summary_content=summary_content)
        self.session.add(newSummary)
        self.session.commit()

    def llm_id_by_name(self, llmName: str) -> int:
        llmTable = self.Base.classes.llm 
        result = self.session.query(llmTable.llm_id).filter(llmTable.llm_name == llmName).first()
        return result[0] if result else None