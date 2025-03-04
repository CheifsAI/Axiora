from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = automap_base()

engine = create_engine("sqlite:///axioradb.db")

Base.prepare(autoload_with=engine)

User = Base.classes.users

session = Session(engine)

all_users = session.query(User).all()

# Iterate through the results and print user information (example)
for user in all_users:
    print(f"Username: {user.username}")