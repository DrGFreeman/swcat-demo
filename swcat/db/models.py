from datetime import date
import uuid

from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel


class Software(SQLModel, table=True):
    software_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    display_name: str = Field(index=True, unique=True)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: str

    releases: list["Release"] = Relationship(
        back_populates="software", cascade_delete=True
    )


class Release(SQLModel, table=True):
    release_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    version: str
    release_date: date

    software_id: uuid.UUID = Field(
        foreign_key="software.software_id", ondelete="CASCADE"
    )
    software: Software = Relationship(back_populates="releases")
