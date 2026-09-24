import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select

# Configuración de base de datos desde variables de entorno
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "app_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# --- MODELOS ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

# --- BASE DE DATOS ---
def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="API Simplificada EC2 + RDS")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- CRUD USUARIOS ---
@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/", response_model=List[User])
def read_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user: raise HTTPException(status_code=404, detail="No encontrado")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, new_data: User, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user: raise HTTPException(status_code=404, detail="No encontrado")
    user.name = new_data.name
    user.email = new_data.email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user: raise HTTPException(status_code=404, detail="No encontrado")
    session.delete(user)
    session.commit()
    return {"message": "Usuario eliminado"}

# --- CRUD LIBROS ---
@app.post("/books/", response_model=Book)
def create_book(book: Book, session: Session = Depends(get_session)):
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/books/", response_model=List[Book])
def read_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()

@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book: raise HTTPException(status_code=404, detail="No encontrado")
    return book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, new_data: Book, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book: raise HTTPException(status_code=404, detail="No encontrado")
    book.title = new_data.title
    book.author = new_data.author
    book.user_id = new_data.user_id
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book: raise HTTPException(status_code=404, detail="No encontrado")
    session.delete(book)
    session.commit()
    return {"message": "Libro eliminado"}

