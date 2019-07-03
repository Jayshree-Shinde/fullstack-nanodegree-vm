from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Project2_databaseSetup import Base, Category, Item, Users


engine = create_engine('sqlite:///catalogapp.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = Users(name="Jayshree Chakraborty", email="jayshreeshinde@udacity.com")
session.add(user1)
session.commit()

user2 = Users(name="Gharesh Shinde", email="ghareshshinde@udacity.com")
session.add(user2)
session.commit()

category1 = Category(id=100, name="Soccer")
session.add(category1)
session.commit()

category2 = Category(id=20, name="Basketball")
session.add(category2)
session.commit()

category3 = Category(id=30, name="Baseball")
session.add(category3)
session.commit()

category4 = Category(id=40, name="Frisbee")
session.add(category4)
session.commit()

category5 = Category(id=50, name="Snowboarding")
session.add(category5)
session.commit()

category6 = Category(id=60, name="Rock Climbing")
session.add(category6)
session.commit()

category7 = Category(id=70, name="Foosball")
session.add(category7)
session.commit()

category8 = Category(id=80, name="Skating")
session.add(category8)
session.commit()

category9 = Category(id=90, name="Hockey")
session.add(category9)
session.commit()

item1 = Item(id=1, name="Soccer Deal", description="It is a \
    good soccer deal", category=category1)
session.add(item1)
session.commit()

item2 = Item(id=2, name="Soccer Master", description="It is a good \
    soccer master game", category=category1)
session.add(item2)
session.commit()
