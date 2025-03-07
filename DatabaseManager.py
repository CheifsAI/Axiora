from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

class DatabaseManager:
    def __init__(self, DATABASE_URL = "sqlite:///axioradb.db"):
        self.engine = create_engine(DATABASE_URL)
        self.Base = automap_base()
        self.Base.prepare(autoload_with=self.engine)
        self.session = Session(self.engine)
    def saveDataSet(self,path,name):
        dataSet = self.Base.classes.data_set
        newDataSet = dataSet(raw_data=path,dataset_name = name)
        self.session.add(newDataSet)
        self.session.flush()
        dataset_id = newDataSet.data_set_id
        self.session.commit()
        return dataset_id
    
    def SaveMetaData(self,id,info,summary,sample,cols):
        metadata = self.Base.metadata
        newMetadata = metadata(data_set_id=id,data_indo=info,data_summary=summary,data_sample=sample,data_columns=cols)
        self.session.add(newMetadata)
        self.session.commit()

    def NewSession(self,user,llm,dataset):
        sessionTable = self.session.session
        newSession = sessionTable(user_id=user,llm_id=llm,data_set_id=dataset)
        self.session.add(newSession)
        self.session.flush()
        session_id = newSession.data_set_id
        self.session.commit()
        return session_id
    def newSum(self,session,summary_content):
        summary = self.session.summary
        newSummary = summary(session_id=session,summary_content=summary_content)
        self.session.add(newSummary)
        self.session.commit()