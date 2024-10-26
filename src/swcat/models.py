from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import UUID4


class SoftwareBase(BaseModel):
    display_name: str = Field(min_length=2)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: EmailStr


class SoftwareCreate(SoftwareBase):
    pass


class Software(SoftwareCreate):
    software_id: UUID4 = Field()
