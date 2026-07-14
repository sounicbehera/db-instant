from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DatabaseEngine = Literal["postgres", "mysql"]


class CreateDatabaseRequest(BaseModel):
    instance_name: str = Field(min_length=3, max_length=120)
    engine_type: DatabaseEngine


class DatabaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    instance_name: str
    engine_type: DatabaseEngine
    username: str
    password: str
    connection_string: str
    allocated_port: int
    status: str
    created_at: datetime