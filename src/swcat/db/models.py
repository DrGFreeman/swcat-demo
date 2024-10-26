import uuid

from sqlmodel import Field
from sqlmodel import SQLModel


class Software(SQLModel, table=True):
    software_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    display_name: str = Field(index=True, unique=True)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: str
