from datetime import date

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import UUID4


class SoftwareBase(BaseModel):
    code_url: HttpUrl | None = Field(default=None)
    description: str | None = Field(default=None, max_length=280)
    display_name: str = Field(min_length=2)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: EmailStr


class SoftwareCreate(SoftwareBase):
    pass


class Software(SoftwareBase):
    software_id: UUID4


class ReleaseBase(BaseModel):
    version: str = Field(min_length=1)
    release_date: date


class ReleaseCreate(ReleaseBase):
    pass


class Release(ReleaseBase):
    release_id: UUID4
    software_id: UUID4
