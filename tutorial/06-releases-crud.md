Similarily to software, we create models for a software release. The `Release` model includes a `software_id` to identify which software the release belongs to.

```python
# swcat/models.py
from datetime import date

...

class ReleaseBase(BaseModel):
    version: str = Field(min_length=1)
    release_date: date


class ReleaseCreate(ReleaseBase):
    pass


class Release(ReleaseBase):
    release_id: UUID4
    software_id: UUID4


class ReleaseUpdate(ReleaseBase):
    version: str | None = Field(default=None, min_length=1)
    release_date: date | None = Field(default=None)
```

We also create the corresponding database model as well as relationships with the `Software` model.

```python
# swcat/db/models.py
from datetime import date

...

class Software(SQLModel, table=True):
    software_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    display_name: str = Field(index=True, unique=True)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: str

    releases: list["Release"] = Relationship(back_populates="software")


class Release(SQLModel, table=True):
    release_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    version: str
    release_date: date

    software_id: uuid.UUID = Field(foreign_key="software.software_id")
    software: Software = Relationship(back_populates="releases")
```

The `releases` field added to the model is a utility field that allows accessing the releases directly from an instance of the `Software` ORM model. It does not impact the table in the database. Restarting the application will automatically create the new release table.

We add the corresponding CRUD API methods (Create, Read (List/Get), Update and Delete).

```python
# swcat/app.py
from swcat.db.models import Release as ReleaseDB
from swcat.models import Release
from swcat.models import ReleaseCreate
from swcat.models import ReleaseUpdate

...

@app.post("/softwares/{software_id}/releases/")
def create_release(
    software_id: UUID4, release: ReleaseCreate, session: SessionDep
) -> Release:
    release_db = ReleaseDB(software_id=software_id, **release.model_dump())

    session.add(release_db)
    session.commit()
    session.refresh(release_db)

    return Release(**release_db.model_dump())


@app.get("/softwares/{software_id}/releases/")
def list_releases(software_id: UUID4, session: SessionDep) -> List[Release]:
    statement = select(ReleaseDB).where(ReleaseDB.software_id == software_id)

    results = session.exec(statement).all()

    return [Release(**rel_db.model_dump()) for rel_db in results]


@app.get("/softwares/{software_id}/releases/{release_id}")
def get_release(software_id: UUID4, release_id: UUID4, session: SessionDep) -> Release:
    release_db = session.exec(
        select(ReleaseDB).where(ReleaseDB.release_id == release_id)
        # Optional since release_id is globally unique
        .where(ReleaseDB.software_id == software_id)
    ).one()

    return Release(**release_db.model_dump())


@app.put("/softwares/{software_id}/releases/{release_id}")
def update_release(
    software_id: UUID4, release_id: UUID4, update: ReleaseUpdate, session: SessionDep
) -> Release:
    release_db = session.exec(
        select(ReleaseDB).where(ReleaseDB.release_id == release_id)
        # Optional since release_id is globally unique
        .where(ReleaseDB.software_id == software_id)
    ).one()

    for field in update.model_fields:
        if (value := getattr(update, field)) is not None:
            setattr(release_db, field, value)

    session.add(release_db)
    session.commit()
    session.refresh(release_db)

    return Release(**release_db.model_dump())


@app.delete("/softwares/{software_id}/releases/{release_id}")
def delete_release(software_id: UUID4, release_id: UUID4, session: SessionDep) -> None:
    release_db = session.exec(
        select(ReleaseDB).where(ReleaseDB.release_id == release_id)
        # Optional since release_id is globally unique
        .where(ReleaseDB.software_id == software_id)
    ).one()

    session.delete(release_db)
    session.commit()
```

Use the API docs to create, list, get, update and delete releases. Verify that multiple release can be created for each software. Verify that releases can be deleted indpendently from other releases and the parent software.

<details>
<summary>`swcat/models.py` Full file</summary>

```python
from datetime import date

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


class ReleaseBase(BaseModel):
    version: str = Field(min_length=1)
    release_date: date


class ReleaseCreate(ReleaseBase):
    pass


class Release(ReleaseBase):
    release_id: UUID4
    software_id: UUID4


class ReleaseUpdate(ReleaseBase):
    version: str | None = Field(default=None, min_length=1)
    release_date: date | None = Field(default=None)
```

</details>

<details>
<summary>`swcat/db/models.py` Full file</summary>

```python
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

    releases: list["Release"] = Relationship(back_populates="software")


class Release(SQLModel, table=True):
    release_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    version: str
    release_date: date

    software_id: uuid.UUID = Field(foreign_key="software.software_id")
    software: Software = Relationship(back_populates="releases")
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

from swcat.db.models import Release as ReleaseDB
from swcat.db.models import Software as SoftwareDB
from swcat.db.utils import get_session
from swcat.db.utils import init_db
from swcat.db.utils import Session
from swcat.models import Release
from swcat.models import ReleaseCreate
from swcat.models import ReleaseUpdate
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
def list_softwares(
    session: SessionDep, display_name: str | None = None
) -> List[Software]:
    statement = select(SoftwareDB)

    if display_name:
        statement = statement.where(SoftwareDB.display_name == display_name)

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


@app.post("/softwares/{software_id}/releases/")
def create_release(
    software_id: UUID4, release: ReleaseCreate, session: SessionDep
) -> Release:
    release_db = ReleaseDB(software_id=software_id, **release.model_dump())

    session.add(release_db)
    session.commit()
    session.refresh(release_db)

    return Release(**release_db.model_dump())


@app.get("/softwares/{software_id}/releases/")
def list_releases(software_id: UUID4, session: SessionDep) -> List[Release]:
    statement = select(ReleaseDB).where(ReleaseDB.software_id == software_id)

    results = session.exec(statement).all()

    return [Release(**rel_db.model_dump()) for rel_db in results]


@app.get("/softwares/{software_id}/releases/{release_id}")
def get_release(software_id: UUID4, release_id: UUID4, session: SessionDep) -> Release:
    release_db = session.exec(
        select(ReleaseDB).where(ReleaseDB.release_id == release_id)
        # Optional since release_id is globally unique
        .where(ReleaseDB.software_id == software_id)
    ).one()

    return Release(**release_db.model_dump())


@app.put("/softwares/{software_id}/releases/{release_id}")
def update_release(
    software_id: UUID4, release_id: UUID4, update: ReleaseUpdate, session: SessionDep
) -> Release:
    release_db = session.exec(
        select(ReleaseDB).where(ReleaseDB.release_id == release_id)
        # Optional since release_id is globally unique
        .where(ReleaseDB.software_id == software_id)
    ).one()

    for field in update.model_fields:
        if (value := getattr(update, field)) is not None:
            setattr(release_db, field, value)

    session.add(release_db)
    session.commit()
    session.refresh(release_db)

    return Release(**release_db.model_dump())


@app.delete("/softwares/{software_id}/releases/{release_id}")
def delete_release(software_id: UUID4, release_id: UUID4, session: SessionDep) -> None:
    release_db = session.exec(
        select(ReleaseDB).where(ReleaseDB.release_id == release_id)
        # Optional since release_id is globally unique
        .where(ReleaseDB.software_id == software_id)
    ).one()

    session.delete(release_db)
    session.commit()
```

</details>