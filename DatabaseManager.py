from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from Axioradb import engine,Dataset,CleanDataset,Report,Summary,LLM, Questions, Dashboards, Charts, ReportMemory
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

    def saveReport(self,rname,user,llm,dataset):
        #sessionTable = self.Base.classes.session
        newReport = Report(user_id=user,
                             llm_id=llm,
                             dataset_id=dataset,
                             report_name=rname)
        self.session.add(newReport)
        self.session.flush()
        report_id = newReport.report_id  
        self.session.commit()
        return report_id
    
    def saveCleanDatasetReport(self, reportId, cleandataset):
        #sessionTable = self.Base.classes.session
        reportRow = self.session.query(Report).filter(Report.report_id == reportId).first()
        if reportRow:
            reportRow.clean_dataset_id = cleandataset
            self.session.commit()

    def saveSummary(self,reportID,summary_content):
        #summary = self.Base.classes.summary
        newSummary = Summary(report_id=reportID,summary_content=summary_content)
        self.session.add(newSummary)
        self.session.commit()

    def llm_id_by_name(self, llmName: str) -> int:
        #llmTable = self.Base.classes.llm 
        result = self.session.query(LLM.llm_id).filter(LLM.llm_name == llmName).first()
        return result[0] if result else None
    
    def llm_installtion_code(self,llmName: str) -> int:
        llm = self.session.query(LLM).filter_by(llm_name=llmName).first()
        return llm.install_llm_code

    
    def saveQuestion(self,reportID, question):
        max_question_num = self.session.query(func.max(Questions.question_num)).filter(Questions.report_id == reportID).scalar()
        if max_question_num is None:
            max_question_num = 0
        new_question_num = max_question_num + 1
        newQu = Questions(question_num = new_question_num, report_id=reportID, question=question)
        self.session.add(newQu)
        self.session.commit()

    def addDashboard(self,reportID):
        newDash = Dashboards(report_id=reportID)
        self.session.add(newDash)
        self.session.flush()
        dashboard_id = newDash.dashboard_id  
        self.session.commit()
        return dashboard_id
    
    def saveCharts(self,dashID,path):
        newChart = Charts(dashboard_id=dashID,chart_path=path)
        self.session.add(newChart)
        self.session.commit()

    def saveMemory(self,reportID,llm,prompet,response,chat):
        newMessage = ReportMemory(report_id=reportID,
                                   llm_id=llm,
                                   prompt=prompet,
                                   response=response,
                                   chat=chat)
        self.session.add(newMessage)
        self.session.commit()

    def get_user_reports(self, user_id):
       reports = self.session.query(Report).filter(Report.user_id == user_id).all()
       return [{'id': report.report_id, 'name': report.report_name} for report in reports]
    
    def get_report_dataset(self, reportID):
        clean_data_set = self.session.query(CleanDataset.raw_data)\
        .join(Report, Report.clean_dataset_id == CleanDataset.clean_dataset_id)\
        .filter(Report.report_id == reportID)\
        .first()
        
        if clean_data_set:
            return clean_data_set[0]
        
        data_set = self.session.query(Dataset.raw_data)\
        .join(Report, Report.dataset_id == Dataset.dataset_id)\
        .filter(Report.report_id == reportID)\
        .first()
        return data_set[0] if data_set else None
    
    def get_report_summary(self, reportID):
        summary = self.session.query(Summary.summary_content).filter(Summary.report_id == reportID).first()
        summary = summary[0] if summary else None
        return summary
    def get_report_questions(self, reportID):
        questions = self.session.query(Questions.question).filter(Questions.report_id == reportID).order_by(Questions.question_num).all()
        return [qu[0] for qu in questions] if questions else None
    
    def get_report_chat(self, reportID):
        chat_history = self.session.query(
            ReportMemory.prompt,
            ReportMemory.response,
            ReportMemory.message_date
        ).filter(
            ReportMemory.report_id == reportID,
            ReportMemory.chat == True
        ).order_by(ReportMemory.message_date).all()
        return chat_history if chat_history else None
    
    def get_report_memory(self, reportID):
        memory = self.session.query(
            ReportMemory.prompt,
            ReportMemory.response,
            ReportMemory.message_date
        ).filter(
            ReportMemory.report_id == reportID,
            ReportMemory.chat == False
        ).order_by(ReportMemory.message_date).all()
        return memory if memory else None

