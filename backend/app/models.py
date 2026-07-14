from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DatabaseInstance(Base):
    __tablename__ = "database_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instance_name: Mapped[str] = mapped_column(String(120), index=True)
    engine_type: Mapped[str] = mapped_column(String(20), index=True)
    username: Mapped[str] = mapped_column(String(80))
    password: Mapped[str] = mapped_column(String(200))
    connection_string: Mapped[str] = mapped_column(String(500))
    allocated_port: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="provisioning")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)