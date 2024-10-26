from typing import Annotated, List
from uuid import UUID

from fastapi import Depends
from fastapi import FastAPI
from sqlmodel import select

from swcat.db import get_session
from swcat.db import init_db
from swcat.db import Session
from swcat.db.models import Software as SoftwareSQL
from swcat.models import Software
from swcat.models import SoftwareCreate

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/softwares/")
def create_software(software: SoftwareCreate, session: SessionDep) -> Software:
    sw_sql = SoftwareSQL(**software.model_dump())
    session.add(sw_sql)
    session.commit()
    session.refresh(sw_sql)
    return Software(**sw_sql.model_dump())


@app.get("/softwares/")
def list_softwares(
    session: SessionDep,
    display_name: str | None = None,
) -> List[Software]:
    stmt = select(SoftwareSQL)

    if display_name:
        stmt = stmt.where(SoftwareSQL.display_name == display_name)

    results = session.exec(stmt).all()

    return [Software(**sw_sql.model_dump()) for sw_sql in results]


@app.get("/softwares/{software_id}")
def get_software(software_id: UUID, session: SessionDep) -> Software:
    sw_sql = session.get(SoftwareSQL, software_id)

    return Software(**sw_sql.model_dump())


@app.put("/softwares/{software_id}")
def update_software(
    software_id: UUID, software: SoftwareCreate, session: SessionDep
) -> Software:
    sw_sql = session.get(SoftwareSQL, software_id)

    for attr in ("display_name", "maintainer_name", "maintainer_email"):
        setattr(sw_sql, attr, getattr(software, attr))

    session.add(sw_sql)
    session.commit()
    session.refresh(sw_sql)

    return Software(**sw_sql.model_dump())


@app.delete("/softwares/{software_id}")
def delete_software(software_id: UUID, session: SessionDep):
    sw_sql = session.get(SoftwareSQL, software_id)

    session.delete(sw_sql)
    session.commit()
