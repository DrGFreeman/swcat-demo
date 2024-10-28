## Database Models (SQL)

Create a `swcat.db` module by creating the `swcat/db/__init__.py` file.

Software DB model (SQL) using SQLModel ORM (combination of SQLAlchemy ORM and Pydantic models).

```python
# swcat/db/models.py
from sqlmodel import Field
from sqlmodel import SQLModel


class Software(SQLModel, table=True):
    software_id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)
    display_name: str = Field(index=True)
    maintainer_name: str | None = Field(default=None)
    maintainer_email: str
```

Remove the default factory from the `Software` model in `swcat/models.py` since the DB model will now take care of generating it.

```python
# swcat/models.py
class Software(SoftwareBase):
    software_id: UUID4
```

## Database Engine & Utilities

```python
# swcat/db/utils.py
from sqlmodel import create_engine
from sqlmodel import Session
from sqlmodel import SQLModel

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = dict(check_same_thread=False)
engine = create_engine(sqlite_url, connect_args=connect_args)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

## Use DB in API and add List Softwares Method

```python
# swcat/app.py
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
```

Refresh the API docs page. Create a software and see that it is returned in the results of the list softwares API method `GET /softwares/` and can be obtained directly from the get software API method `GET /softwares/{software_id}`.

In the context of this tutorial, we do not implement pagination of the list softwares method. However, in a production grade API, all methods listing collections should implement pagination.
