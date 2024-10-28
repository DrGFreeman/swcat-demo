## Prevent Duplicate Software Names

There is currently nothing preventing the creation of two software entries with the same name (either through creation or update). There are different ways to enforce uniqueness of software names. One of them is to set a uniqueness constraint on the `display_name` column in the database.

Modify the `Software` DB model in `swcat/db/models.py`.

```python
# swcat/db/models.py
class Software(SQLModel, table=True):
    software_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    display_name: str = Field(index=True, unique=True)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: str
```

Modification to an existing table in the in an existing database without data loss cannot be done with the `SQLModel.metadata.create_all(engine)` statement in the `swcat.db.utils.init_db()` function and require the use of a database schema migration tool such as [alembic](https://alembic.sqlalchemy.org/en/latest/index.html). This topic is beyond the scope of this turorial. As a workaround we can simply delete the `database.db` file, or use an external tool to drop the `software` table in the database (either way, the data will be lost).

Once the database is deleted, restart the application.

Use the API docs to add a software, then try to create a new software with the same name. The API returns a 500 status code (Internal Server Error). Looking at the server logs, we can see that the database is rejecting the non-unique display name with a SQLAlchemy `IntegrityError` (below).

```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: software.display_name
[SQL: INSERT INTO software (software_id, display_name, maintainer_name, maintainer_email) VALUES (?, ?, ?, ?)]
[parameters: ('a42a3d4b7731422d80e1036749144990', 'RPA Core', 'string', 'user@example.com')]
(Background on this error at: https://sqlalche.me/e/20/gkpj)
```

In a production grade API, we would capture the exception and return an appropriate error code, e.g. a Client Error with [status code 409 "Conflict"](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409). 

<details>
<summary>`swcat/db/models.py` Full file</summary>

```python
import uuid

from sqlmodel import Field
from sqlmodel import SQLModel


class Software(SQLModel, table=True):
    software_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    display_name: str = Field(index=True, unique=True)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: str
```

</details>

## List Softwares by Name

We might also want to be able to list (search) softwares for a specific name. We already created an index on the `.display_name` column in the `Software` DB model in `swcat/db/models.py`.

We add a `display_name` optional query string parameter to the List Softwares API method and implement the associated filtering in the method body. Note that even though the display name is unique, and therefore only one software will be returned, we keep the response in a list to respect the semaintics of the "list" API method.

```python
@app.get("/softwares/")
def list_softwares(display_name: str | None, session: SessionDep) -> List[Software]:
    statement = select(SoftwareDB)

    if display_name:
        statement = statement.where(SoftwareDB.display_name == display_name)

    results = session.exec(statement).all()

    return [Software(**sw_db.model_dump()) for sw_db in results]
```

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
```

</details>
