from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import DatabaseInstance
from app.schemas import CreateDatabaseRequest, DatabaseResponse
from app.services.credentials import generate_password, generate_username

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DB-Instant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/databases", response_model=list[DatabaseResponse])
def list_databases(db: Session = Depends(get_db)):
    return db.scalars(select(DatabaseInstance).order_by(DatabaseInstance.id.desc())).all()


@app.post(
    "/api/databases",
    response_model=DatabaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_database(payload: CreateDatabaseRequest, db: Session = Depends(get_db)):
    username = generate_username()
    password = generate_password()
    allocated_port = next_available_port(db, payload.engine_type)

    if payload.engine_type == "postgres":
        connection_string = (
            f"postgresql://{username}:{password}@localhost:{allocated_port}/{payload.instance_name}"
        )
    else:
        connection_string = (
            f"mysql://{username}:{password}@localhost:{allocated_port}/{payload.instance_name}"
        )

    database = DatabaseInstance(
        instance_name=payload.instance_name,
        engine_type=payload.engine_type,
        username=username,
        password=password,
        connection_string=connection_string,
        allocated_port=allocated_port,
        status="provisioning",
    )

    db.add(database)
    db.commit()
    db.refresh(database)
    return database


@app.delete("/api/databases/{database_id}")
def delete_database(database_id: int, db: Session = Depends(get_db)):
    database = db.get(DatabaseInstance, database_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Database instance not found")

    db.delete(database)
    db.commit()
    return {"deleted": database_id}


def next_available_port(db: Session, engine_type: str) -> int:
    base_port = 54000 if engine_type == "postgres" else 33000
    used_ports = set(db.scalars(select(DatabaseInstance.allocated_port)).all())
    candidate = base_port + 1

    while candidate in used_ports:
        candidate += 1

    return candidate