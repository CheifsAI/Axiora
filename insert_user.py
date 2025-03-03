from sqlalchemy.orm import sessionmaker
from Axioradb import engine,users,LLM

Session = sessionmaker(bind=engine)
session = Session()



llm_list = session.query(LLM).all()

# Print the users
for user in llm_list:
    print(user)
    
session.close()
