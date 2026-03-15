from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "todos.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'medium'
            )
        """)

init_db()

class TodoCreate(BaseModel):
    title: str
    priority: Optional[str] = "medium"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

@app.get("/todos")
def get_todos():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO todos (title, priority) VALUES (?, ?)",
            (todo.title, todo.priority)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM todos WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)

@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id=?", (todo_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")
        fields = {k: v for k, v in todo.dict().items() if v is not None}
        if fields:
            sets = ", ".join(f"{k}=?" for k in fields)
            conn.execute(f"UPDATE todos SET {sets} WHERE id=?", (*fields.values(), todo_id))
            conn.commit()
        return dict(conn.execute("SELECT * FROM todos WHERE id=?", (todo_id,)).fetchone())

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id=?", (todo_id,))
        conn.commit()
