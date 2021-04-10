from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Global Variables

SQLITE = 'sqlite'
MYSQL = 'mysql'

Base = declarative_base()


class City(Base):
    __tablename__ = 'city'

    name = Column(String(50), primary_key=True)
    persons = relationship('Person')


class State(Base):
    __tablename__ = 'states'

    short_name = Column(String(3), primary_key=True)
    full_name = Column(String(length=50))
    persons = relationship('Person', backref='state')


class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))
    state_short = Column(String(3), ForeignKey('states.short_name'))
    city = Column(String(50), ForeignKey('city.name'))

class Db:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}',
        MYSQL: 'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@localhost/{DB}'
    }

    def __init__(self, dbtype='sqlite', username='', password='', dbname='persons'):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname, USERNAME=username, PASSWORD=password)
            self.engine = create_engine(engine_url, echo=False)
        else:
            print('DBType is not found in DB_ENGINE')

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def read_all(self, order = Person.name):
        try:
            result = self.session.query(Person).order_by(order).all()
            return result
        except:
            return False

    def read_by_id(self, id):
        try:
            result = self.session.query(Person).get(id)
            return result
        except:
            return False

    def read_by_state(self, state='CZE'):
        # self.session.query(Person).join(State).filter(or_(State.full_name.like('%b%'), Person.name.like('%a%'))).order_by(desc(State.short_name)).limit(2).all()
        try:
            result = self.session.query(Person).join(State).filter(State.short_name.like(f'%{state}%')).order_by(Person.name).all()
            return result
        except:
            return False

    def read_states(self):
        try:
            result = self.session.query(State).all()
            return result
        except:
            return False

    def read_cities(self):
        try:
            result = self.session.query(City).all()
            return result
        except:
            return False

    def create(self, person):
        try:
            self.session.add(person)
            self.session.commit()
            return True
        except:
            return False

    def update(self):
        try:
            self.session.commit()
            return True
        except:
            return False

    def delete(self, id):
        try:
            person = self.read_by_id(id)
            self.session.delete(person)
            self.session.commit()
            return True
        except:
            return False

    def create_state(self, state):
        try:
            self.session.add(state)
            self.session.commit()
            return True
        except:
            return False

    def create_city(self, city):
        try:
            self.session.add(city)
            self.session.commit()
            return True
        except:
            return False
