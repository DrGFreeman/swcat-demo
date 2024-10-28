## Update and Delete Software

Create a model for a software update. It uses the same fields as `SoftwareBase` but all fields are optional.

```python
# swcat/models.py
class SoftwareUpdate(SoftwareBase):
    display_name: str | None = Field(default=None, min_length=2)
    maintainer_email: EmailStr | None = Field(default=None)
```

Add the Update Software and Delete Software methods to the API.

```python
# swcat/app.py
from swcat.models import SoftwareUpdate

...

@app.put("/softwares/{software_id}")
def update_software(
    software_id: UUID4, update: SoftwareUpdate, session: SessionDep
) -> Software:
    software_db = session.get(SoftwareDB, software_id)

    for field in update.model_fields:
        if (value := getattr(update, field)) is not None:
            setattr(software_db, field, value)

    session.add(software_db)
    session.commit()
    session.refresh(software_db)

    return Software(**software_db.model_dump())


@app.delete("/softwares/{software_id}")
def delete_software(software_id: UUID4, session: SessionDep) -> None:
    software_db = session.get(SoftwareDB, software_id)

    session.delete(software_db)
    session.commit()
```

<details>
<summary>`swcat/models.py` Full file</summary>

```python
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
    software_id: UUID4


class SoftwareUpdate(SoftwareBase):
    display_name: str | None = Field(default=None, min_length=2)
    maintainer_email: EmailStr | None = Field(default=None)
```

</details>

<details>
<summary>`swcat/app.py` Full file</summary>

```python
from typing import Annotated, List

from fastapi import Depends
from fastapi import FastAPI
from pydantic import UUID4
from sqlmodel import select

from swcat.db.models import Software as SoftwareDB
from swcat.db.utils import get_session
from swcat.db.utils import init_db
from swcat.db.utils import Session
from swcat.models import Software
from swcat.models import SoftwareCreate
from swcat.models import SoftwareUpdate

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/softwares/")
def create_software(software: SoftwareCreate, session: SessionDep) -> Software:
    software_db = SoftwareDB(**software.model_dump())

    session.add(software_db)
    session.commit()
    session.refresh(software_db)

    return Software(**software_db.model_dump())


@app.get("/softwares/")
def list_softwares(session: SessionDep) -> List[Software]:
    statement = select(SoftwareDB)

    results = session.exec(statement).all()

    return [Software(**sw_db.model_dump()) for sw_db in results]


@app.get("/softwares/{software_id}")
def get_software(software_id: UUID4, session: SessionDep) -> Software:
    software_db = session.get(SoftwareDB, software_id)

    return Software(**software_db.model_dump())


@app.put("/softwares/{software_id}")
def update_software(
    software_id: UUID4, update: SoftwareUpdate, session: SessionDep
) -> Software:
    software_db = session.get(SoftwareDB, software_id)

    for field in update.model_fields:
        if (value := getattr(update, field)) is not None:
            setattr(software_db, field, value)

    session.add(software_db)
    session.commit()
    session.refresh(software_db)

    return Software(**software_db.model_dump())


@app.delete("/softwares/{software_id}")
def delete_software(software_id: UUID4, session: SessionDep) -> None:
    software_db = session.get(SoftwareDB, software_id)

    session.delete(software_db)
    session.commit()
```

</details>
