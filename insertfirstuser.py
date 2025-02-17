from sqlalchemy.orm import sessionmaker
from Axioradb import engine,users

Session = sessionmaker(bind=engine)
session = Session()

users_list = session.query(users).all()

# Print the users
for user in users_list:
    print(user)

session.close()
