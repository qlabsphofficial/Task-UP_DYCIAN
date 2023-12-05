from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from pydantic import Field, BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import models


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    student_id: str
    password: str
    first_name: str
    last_name: str
    middle_initial: str
    status: str
    department: str
    course: str

class UserID(BaseModel):
    id: int


class NoteID(BaseModel):
    id: int

class LoginData(BaseModel):
    student_id: str
    password: str

class Note(BaseModel):
    note_title: str
    note_due: str
    note_description: str
    note_owner: int


class Task(BaseModel):
    task_type: str
    task_description: str
    due_date: str
    task_owner: int


class TaskID(BaseModel):
    task_id: int



def get_db():
    try:
        db = SessionLocal(bind=engine)
        yield db
    finally:
        db.close()

@app.post('/register')
async def register(user: User, db: Session = Depends(get_db)):
    new_user = models.User()

    try:
        new_user.student_id = user.student_id
        new_user.password = user.password
        new_user.first_name = user.first_name
        new_user.last_name = user.last_name
        new_user.middle_initial = user.middle_initial
        new_user.status = user.status
        new_user.department = user.department
        new_user.course = user.course

        db.add(new_user)
        db.commit()

    finally:
        db.close()

    return {'response': 'success'}


@app.post('/login')
async def login(student: LoginData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.student_id == student.student_id).first()
    print(user)

    if user.password == student.password:
        return {'response': 'login success', 'user_id': user.id}
    else:
        return {'response': 'login failed'}


@app.post('/get_user_data')
async def get_user_data(user_id: UserID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id.id).first()

    return {'user_data': user, 'response': 'retrieval success'}


@app.get('/get_notes')
async def get_notes(id: str, db: Session = Depends(get_db)):
    try:
        all_notes = db.query(models.Note).filter(models.Note.note_owner == id).all()
        print(all_notes)

        return {'response': 'retrieval complete.', 'notes': all_notes}
    except:
        print('Retrieval failed.')
        return {'response': 'retrieval failed.', 'notes': all_notes}


@app.post('/create_note')
async def create_note(note: Note, db: Session = Depends(get_db)):
    new_note = models.Note()

    to_datetime = note.note_due[:25]
    date_format = "%m-%d-%Y %H:%M"

    new_note.note_title = note.note_title
    new_note.due_date = datetime.strptime(to_datetime, date_format)
    new_note.note_description = note.note_description
    new_note.note_owner = int(note.note_owner)

    db.add(new_note)
    db.commit()

    return {'response': 'note created.'}
    # except:
    #     return {'response': 'failed to create note.'}
    

@app.post('/delete_note')
async def delete_note(note_id: NoteID, db: Session = Depends(get_db)):
    try:
        retrieved_note = db.query(models.Note).filter(models.Note.id == note_id.id).first()
        
        if retrieved_note:
            db.delete(retrieved_note)
            db.commit()

        return {'response': 'note deleted.'}
    except:
        return {'response': 'failed to delete note.'}
    

@app.get('/get_tasks')
async def get_tasks(id: str, db: Session = Depends(get_db)):
    try:
        all_tasks = db.query(models.Task).filter(models.Task.task_owner == id)

        all_activities = []
        all_exams = []

        for task in all_tasks:
            task.due_date = task.due_date.strftime("%Y-%m-%d %H:%M")

            if task.task_type == 'Activities':
                all_activities.append(task)
            else:
                all_exams.append(task)

        return {'response': 'tasks retrieved', 'activities': all_activities, 'exams': all_exams}
    except:
        return {'response': 'failed to retrieve tasks.'}
    

@app.get('/get_task_overview')
async def get_task_overview(id: str, db: Session = Depends(get_db)):
    # try:
        all_tasks = db.query(models.Task).filter(models.Task.task_owner == id)

        all_activities = []
        all_exams = []
        weekly_tasks = []
        completed_tasks = 0
        pending_tasks = 0

        for task in all_tasks:
            task.due_date = task.due_date.strftime("%Y-%m-%d %H:%M")

            if task.task_type == 'Activities':
                all_activities.append(task)
            else:
                all_exams.append(task)

            # Handling Pending and Completed Tasks
            if task.is_completed:
                completed_tasks += 1
            else:
                pending_tasks += 1

        return {
            'response': 'tasks retrieved', 
            'activities': all_activities,
            'exams': all_exams,
            'weekly_tasks': weekly_tasks,
            'completed': completed_tasks,
            'pending': pending_tasks
        }
    # except:
    #     return {'response': 'failed to retrieve tasks.'}


@app.post('/create_task')
async def create_task(task: Task, db: Session = Depends(get_db)):
    new_task = models.Task()

    to_datetime = task.due_date[:25]
    date_format = "%m-%d-%Y %H:%M"

    new_task.task_type = task.task_type
    new_task.task_description = task.task_description
    new_task.due_date = datetime.strptime(to_datetime, date_format)
    new_task.task_owner = task.task_owner
    new_task.is_completed = False
    
    print(f'Task type: {new_task.task_type}')
    print(f'Task desc: {new_task.task_description}')
    print(f'Task date: {new_task.due_date}')
    print(f'Task owner: {new_task.task_owner}')
    print(f'Task status: {new_task.is_completed}')
    db.add(new_task)
    db.commit()

    return {'response': 'task created'}


@app.post('/mark_complete')
async def mark_task_complete(task: TaskID, db: Session = Depends(get_db)):
    try:
        retrieved_task = db.query(models.Task).filter(models.Task.id == task.task_id).first()
        
        if retrieved_task:
            retrieved_task.is_completed = True
            db.commit()

        return {'response': 'task completed.'}
    except:
        return {'response': 'failed to mark task as completed.'}