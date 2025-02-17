from sqlalchemy.orm import sessionmaker
from Axioradb import engine,users

Session = sessionmaker(bind=engine)
session = Session()

maro = users(username='maro', email='maro@gmail.com', password='202425')
cheif = users(username='cheif', email='cheifs@gmail.com', password='12345')

session.add(maro)
session.add(cheif)

session.commit()

users_list = session.query(users).all()

# Print the users
for user in users_list:
    print(user)
    
session.close()
