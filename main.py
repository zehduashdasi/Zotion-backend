import fastapi
import sqlite3 as sq
import fastapi.middleware
import fastapi.middleware.cors
from pydantic import BaseModel
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

secretkey = os.getenv("secretkey")


def encode_jwt(payload):
    return jwt.encode(payload, secretkey, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, secretkey, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise fastapi.HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise fastapi.HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))


app = fastapi.FastAPI()

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

class Login(BaseModel):
    username: str
    password: str

class Register(BaseModel):
    username: str
    password: str

class ToDo(BaseModel):
    title: str
    content: str
    token: str

class ToDoEdit(BaseModel):
    id: int
    title: str
    content: str
    token: str

class ToDoDelete(BaseModel):
    id: int
    token: str

@app.post("/login/")
def login(cred: Login):
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id,username FROM users WHERE username = ? AND password = ?",(cred.username, cred.password))
        result = cursor.fetchone()
        if result:
            return {"token":encode_jwt({"id":result[0],"username":result[1]}),"id":result[0]}
        else:
            raise fastapi.HTTPException(401,"user not found")
    except fastapi.HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(e)
        raise fastapi.HTTPException(status_code=500,detail=str(e))
    finally:
        conn.close()

@app.post("/register/")
def register(cred: Register):
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?",(cred.username,))
        if cursor.fetchone():
            print("username already exists")
            raise fastapi.HTTPException(status_code = 401, detail = "username already exists")
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",(cred.username, cred.password))
        conn.commit()
        cursor.execute("SELECT id,username FROM users WHERE username = ?",(cred.username,))
        result = cursor.fetchone()
        return {"token": encode_jwt({"id":result[0], "username":result[1]}),"id":result[0]}
    except fastapi.HTTPException:
        raise 
    except Exception as e:
        conn.rollback()
        print(e)
        raise fastapi.HTTPException(status_code=500,detail=str(e))
    finally:
        conn.close()

@app.get("/todo/{user_id}/")
def get_todos(user_id: int, token: str):
    try:
        conn = sq.connect("database.db")
        conn.row_factory = sq.Row
        cursor = conn.cursor()

        token_user_id = decode_jwt(token)["id"]

        if not token_user_id == user_id:
            raise fastapi.HTTPException(status_code=401, detail="not authorized")
        
        cursor.execute("SELECT id, title, content FROM todo WHERE user = ?",(user_id,))
        return cursor.fetchall()
    except fastapi.HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(e)
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/add_todo/")
def add_todo(todo: ToDo):
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()

        token_user_id = decode_jwt(todo.token)['id']

        cursor.execute("INSERT INTO todo (user, title, content) VALUES (?, ?, ?)",(token_user_id, todo.title, todo.content))
        conn.commit()
        return {"detail":"done"}
    except fastapi.HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(e)
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/edit_todo/")
def edit_todo(todo: ToDoEdit):
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT user FROM todo WHERE id = ?",(todo.id,))
        token_user_id = decode_jwt(todo.token)['id']
        user_id = cursor.fetchone()
        if not user_id:
            raise fastapi.HTTPException(status_code=404, detail="todo list does not exist")
        if not token_user_id == user_id[0]:
            raise fastapi.HTTPException(status_code=401, detail="not authorized")

        cursor.execute("UPDATE todo SET title=?, content=? WHERE id=?",(todo.title,todo.content,todo.id))
        conn.commit()
    except fastapi.HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(e)
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/delete_todo/")
def delete_todo(todo: ToDoDelete):
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT user FROM todo WHERE id = ?",(todo.id,))
        token_user_id = decode_jwt(todo.token)['id']
        user_id = cursor.fetchone()
        if not user_id:
            raise fastapi.HTTPException(status_code=404, detail="todo list does not exist")
        if not token_user_id == user_id[0]:
            raise fastapi.HTTPException(status_code=401, detail="not authorized")
        
        cursor.execute("DELETE FROM todo WHERE id=?",(todo.id,))
        conn.commit()
    except fastapi.HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(e)
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()