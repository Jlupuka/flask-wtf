import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    surname: Mapped[Optional[str]]
    name: Mapped[Optional[str]]
    age: Mapped[Optional[int]]
    position: Mapped[Optional[str]]
    speciality: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    hashed_password: Mapped[Optional[str]]
    modified_date: Mapped[Optional[datetime.datetime]]
    jobs: Mapped['Jobs'] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return f'<Colonist> {self.id} {self.name} {self.surname}'


class Jobs(SqlAlchemyBase):
    __tablename__ = 'jobs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_leader: Mapped[int] = mapped_column(ForeignKey(User.id))
    job: Mapped[Optional[str]]
    work_size: Mapped[Optional[int]]
    collaborators: Mapped[Optional[str]]
    start_date: Mapped[Optional[datetime.datetime]]
    end_date: Mapped[Optional[datetime.datetime]]
    is_finished: Mapped[Optional[bool]]
    user: Mapped['User'] = relationship(back_populates='jobs')
