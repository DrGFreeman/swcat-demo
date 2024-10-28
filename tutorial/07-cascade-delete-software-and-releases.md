In the previous section, we created releases and deleted them independently from each other and from the parent software. What if we try to delete a software for which releases are defined? If we try it, the API returns a 500 status code "Internal Server Error". Looking at the server logs, we see that the database refuses to delete the software because the `software_id` column of the release table is not allowd to be empty (`NULL`).

```
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: release.software_id
[SQL: UPDATE release SET software_id=? WHERE release.release_id = ?]
[parameters: [(None, '0285b56a437d45ff8f344256d63f25f4'), (None, '4338875445c5418d990506448a1666e5')]]
(Background on this error at: https://sqlalche.me/e/20/gkpj)
```

We could allow this field to be `None` in the `Relase` model in `swcat/db/models.py`. This would allow deletion of the parent software but would leave "orphan" release(s) in the database.

In this case, we would prefer that the deletion of the parent software triggers the deletion of the associated releases. This is called **cascade** deletion. There are different ways to configure cascade deletion that depend on the database backend used (see the [SQLModel documentation](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/cascade-delete-relationships/) for details). For simplicity, we set both the `cascade_delete=True` attribute in the `release` `Relationship` of the `Software` DB model and the `ondelete="CASCADE"` on the `software_id` `Field` of the `Release` DB model in `swcat/db/models.py`.

```python
# swcat/db/models.py
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
```

Since we are modifying existing tables and we havent setup a migration management tool, we need to delete the `database.db` database file and restart the application for the changes to be applied to the database tables.

After restarting the application, create a new software with two or more releases. Verify that deleting a release deletes the release without deleting the parent software. Then delete the software. Verify that there are no exceptions raised this time and that the software is deleted. Using a separate database management tool, verify that the associated releases have also been deleted from the release table.

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
```

</details>