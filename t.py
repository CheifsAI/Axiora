from DatabaseManager import DatabaseManager
db = DatabaseManager()
#print(db.get_report_dataset(1))
#print(db.get_report_summary(2))
if db.get_report_summary(2):
        print(db.get_report_summary(1))
