from DatabaseManager import DatabaseManager
db = DatabaseManager()
#print(db.get_report_dataset(1))
#print(db.get_report_summary(2))
#print(db.get_report_questions(2))
chat_history = db.get_report_memory(1)
for prompt, response, _ in chat_history:
    if response:
        print(response)
#print(db.get_report_memory(2))
#if db.get_report_summary(2):
#        print(db.get_report_summary(1))
#from OprFuncs import read_file
#import pandas as pd
#df = read_file("Test_Datasets\laptop_price.csv")
#df = pd.read_csv("Test_Datasets\laptop_price.csv", encoding='latin1')
#print(df.head(3))