from sqlalchemy.orm import sessionmaker
from Axioradb import *

Session = sessionmaker(bind=engine)
session = Session()

new_user = User(username="cheif", password="12345", email="cheif@gmail.com")

# Add the new user to the session
session.add(new_user)

# Commit the transaction to save the new user to the database
session.commit()


user_list = session.query(User).all()

# Print the users
for user in user_list:
    print(user)
    
session.close()
