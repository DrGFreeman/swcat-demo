from typing import Annotated, List, Literal
from uuid import UUID

from fastapi import Depends
from fastapi import FastAPI
from sqlmodel import select

from swcat.db import get_session
from swcat.db import init_db
from swcat.db import Session
from swcat.db.models import Release as ReleaseSQL
from swcat.db.models import Software as SoftwareSQL
from swcat.models import Release
from swcat.models import ReleaseCreate
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


@app.post("/softwares/{software_id}/releases/")
def create_release(
    software_id: UUID, release: ReleaseCreate, session: SessionDep
) -> Release:
    rel_sql = ReleaseSQL(software_id=software_id, **release.model_dump())

    session.add(rel_sql)
    session.commit()
    session.refresh(rel_sql)

    return Release(**rel_sql.model_dump())


@app.get("/softwares/{software_id}/releases/")
def list_releases(
    software_id: UUID | Literal["-"], session: SessionDep
) -> List[Release]:
    stmt = select(ReleaseSQL)

    if software_id != "-":
        stmt = stmt.where(ReleaseSQL.software_id == software_id)

    results = session.exec(stmt).all()

    return [Release(**rel_sql.model_dump()) for rel_sql in results]


@app.get("/softwares/{software_id}/releases/{release_id}")
def get_release(software_id: UUID, release_id: UUID, session: SessionDep) -> Release:
    rel_sql = session.exec(
        select(ReleaseSQL)
        .where(ReleaseSQL.release_id == release_id)
        .where(ReleaseSQL.software_id == software_id)
    ).one()

    return Release(**rel_sql.model_dump())


@app.delete("/softwares/{software_id}/releases/{release_id}")
def delete_release(software_id: UUID, release_id: UUID, session: SessionDep):
    rel_sql = session.exec(
        select(ReleaseSQL)
        .where(ReleaseSQL.release_id == release_id)
        .where(ReleaseSQL.software_id == software_id)
    ).one()

    session.delete(rel_sql)
    session.commit()
