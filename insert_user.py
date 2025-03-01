from sqlalchemy.orm import sessionmaker
from Axioradb import engine,users,LLM

Session = sessionmaker(bind=engine)
session = Session()

llama3b = LLM(llm_name='llama3.2:3b', parameters='3', install_llm_code='ollama run llama3.2')

session.add(llama3b)

session.commit()

llm_list = session.query(LLM).all()

# Print the users
for user in llm_list:
    print(user)
    
session.close()
