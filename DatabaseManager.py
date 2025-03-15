from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from Axioradb import engine,Dataset,CleanDataset,Session,Summary,LLM, Questions, Dashboards, Charts, SessionMemory
from sqlalchemy import func

class DatabaseManager:
    def __init__(self):
        SessionLocal = sessionmaker(bind=engine)
        self.session = SessionLocal()

    def saveDataSet(self,path,name,info,summary,sample,cols):
        #dataSet = self.Base.classes.dataset
        newDataSet = Dataset(raw_data=path,
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
    def saveCleanDataset(self,ogID,path,name,info,summary,sample,cols):
        #cleandataset = self.Base.classes.cleanDataset
        newCleanDataset = CleanDataset(original_dataset_id=ogID,
                            raw_data=path,
                            #uploaded_at=datetime.now(),
                             dataset_name = name,
                             data_info=info,
                             data_summary=summary,
                             data_sample=sample,
                             data_columns=cols)
        self.session.add(newCleanDataset)
        self.session.flush()
        clean_dataset_id = newCleanDataset.clean_dataset_id
        self.session.commit()
        return clean_dataset_id

    def saveSession(self,user,llm,dataset):
        #sessionTable = self.Base.classes.session
        newSession = Session(user_id=user,
                             llm_id=llm,
                             dataset_id=dataset)
        self.session.add(newSession)
        self.session.flush()
        session_id = newSession.session_id  
        self.session.commit()
        return session_id
    
    def saveCleanSession(self, sessId, cleandataset):
        #sessionTable = self.Base.classes.session
        sessionRow = self.session.query(Session).filter(Session.session_id == sessId).first()
        if sessionRow:
            sessionRow.clean_dataset_id = cleandataset
            self.session.commit()

    def saveSummary(self,session,summary_content):
        #summary = self.Base.classes.summary
        newSummary = Summary(session_id=session,summary_content=summary_content)
        self.session.add(newSummary)
        self.session.commit()

    def llm_id_by_name(self, llmName: str) -> int:
        #llmTable = self.Base.classes.llm 
        result = self.session.query(LLM.llm_id).filter(LLM.llm_name == llmName).first()
        return result[0] if result else None
    
    def saveQuestion(self,sessID, question):
        max_question_num = self.session.query(func.max(Questions.question_num)).filter(Questions.session_id == sessID).scalar()
        if max_question_num is None:
            max_question_num = 0
        new_question_num = max_question_num + 1
        newQu = Questions(question_num = new_question_num, session_id=sessID, question=question)
        self.session.add(newQu)
        self.session.commit()

    def addDashboard(self,sessID):
        newDash = Dashboards(session_id=sessID)
        self.session.add(newDash)
        self.session.flush()
        dashboard_id = newDash.dashboard_id  
        self.session.commit()
        return dashboard_id
    
    def saveCharts(self,dashID,path):
        newChart = Charts(dashboard_id=dashID,chart_path=path)
        self.session.add(newChart)
        self.session.commit()

    def saveMemory(self,sessID,llm,prompet,response,chat):
        newMessage = SessionMemory(session_id=sessID,
                                   llm_id=llm,
                                   prompt=prompet,
                                   response=response,
                                   chat=chat)
        self.session.add(newMessage)
        self.session.commit()
