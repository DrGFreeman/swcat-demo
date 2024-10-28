## Models for Software

We define models (schemas) for the creation and representation of a softwade in the catalog using pydantic. We place these models in a file named `swcat/models.py`.

```python
# swcat/models.py
import uuid

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


class Software(SoftwareBase):
    software_id: UUID4 = Field(default_factory=uuid.uuid4)
```


## API Application Setup & Create Software Method

```python
# swcat/app.py
from fastapi import FastAPI

from swcat.models import Software
from swcat.models import SoftwareCreate

app = FastAPI()


@app.post("/softwares/")
def create_software(software: SoftwareCreate) -> Software:
    return Software(**software.model_dump())
```

Run the application with

```
fastapi dev swcat/app.py
```

And open the API docs at http://127.0.0.1:8000/docs.

Use "Try it out" on the `POST /softwares/` method.

This works but the changes are not persistent... We need to store the created software entries in a database.