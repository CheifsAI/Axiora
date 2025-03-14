from sqlalchemy.orm import sessionmaker
from Axioradb import *

Session = sessionmaker(bind=engine)
session = Session()

llama = LLM(llm_name="llama3.2:3b", parameters=3, install_llm_code="ollama run llama3.2:3b")
phi = LLM(llm_name="phi3.5:3.8b", parameters=3.8, install_llm_code="ollama run phi3.5:3.8b")
mina = User(username="mina", password="7788", email="mina@gmail.com")
huss = User(username="huss", password="1020", email="huss@gmail.com")
cheif = User(username="cheif", password="12345", email="cheif@gmail.com")
# Add the new user to the session
session.add(llama)
session.add(phi)
session.add(mina)
session.add(huss)
session.add(cheif)


# Commit the transaction to save the new user to the database
session.commit()


user_list = session.query(User).all()
llm_list = session.query(LLM).all()


# Print the users
for user in user_list:
    print(user)
for llm in llm_list:
    print(llm)
    
session.close()
