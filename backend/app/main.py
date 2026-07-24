from fastapi import FastAPI
from pydantic import BaseModel
from secrets import token_urlsafe
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DB-Instant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DatabaseEngine = Literal["postgres", "mysql"]

class CreateDatabaseRequest(BaseModel):
    instance_name: str
    engine_type: DatabaseEngine

class DatabaseResponse(BaseModel):
    id: int
    instance_name: str
    engine_type: DatabaseEngine
    username: str
    password: str
    connection_string: str
    status: str

databases: list[DatabaseResponse] = []

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/databases")
def list_databases():
    return databases

@app.post("/api/databases", response_model=DatabaseResponse)
def create_database(payload: CreateDatabaseRequest):
    db_id = len(databases) + 1
    username = f"dev_{token_urlsafe(4)}"
    password = token_urlsafe(16)
    port = 54000 + db_id if payload.engine_type == "postgres" else 33000 + db_id

    connection_string = (
        f"postgresql://{username}:{password}@localhost:{port}/{payload.instance_name}"
        if payload.engine_type == "postgres"
        else f"mysql://{username}:{password}@localhost:{port}/{payload.instance_name}"
    )

    database = DatabaseResponse(
        id=db_id,
        instance_name=payload.instance_name,
        engine_type=payload.engine_type,
        username=username,
        password=password,
        connection_string=connection_string,
        status="provisioning",
    )

    databases.append(database)
    return database

@app.delete("/api/databases/{database_id}")
def delete_database(database_id: int):
    global databases
    databases = [db for db in databases if db.id != database_id]
    return {"deleted": database_id}