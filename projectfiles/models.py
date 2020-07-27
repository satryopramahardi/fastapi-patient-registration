from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy import func
from sqlalchemy.orm import relationship

from projectfiles.database import Base


class RootCause(Base):  
    __tablename__ = 'root_cause'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Bug(Base):  
    __tablename__ = 'bug'
    id = Column(Integer, primary_key=True)
    root_cause_id = Column(ForeignKey('root_cause.id'),
                           nullable=False,
                           index=True)
    bug_tracker_url = Column(String(255), unique=True)
    who = Column(String(255))
    when = Column(DateTime, default=func.now())

    root_cause = relationship(RootCause)

    def __repr__(self):
        return 'id: {}, root cause: {}'.format(self.id, self.root_cause.name)

class Patient(Base):
    __tablename__= "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(40), nullable= False, unique=True)
    password = Column(String(72), nullable = False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    birth_date = Column(Date, nullable=True)
