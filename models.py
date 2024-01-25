from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Boolean, String, Column, ForeignKey, DateTime, LargeBinary


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
    birthday = Column(String)

    notes = relationship('Note', back_populates='owner')
    tasks = relationship('Task', back_populates='task_setter')

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    note_title = Column(String)
    note_description = Column(String)
    note_owner = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notes")
    attachments = relationship("Attachment", back_populates="note_bound")


class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String)
    bind_note = Column(Integer, ForeignKey('notes.id'))

    note_bound = relationship('Note', back_populates="attachments")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String)
    task_description = Column(String)
    due_date = Column(DateTime)
    is_completed = Column(Boolean)
    task_owner = Column(Integer, ForeignKey("users.id"))

    task_setter = relationship("User", back_populates="tasks")