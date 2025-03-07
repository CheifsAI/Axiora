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
    def SaveMetaData(self,id):
        dataset_metadata = self.Base.dataset_metadata
