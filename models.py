from database import Base
from sqlalchemy import Integer, Boolean, String, Column


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    middle_initial = Column(String)
    contact = Column(String)
    status = Column(String)
    department = Column(String)
    course = Column(String)