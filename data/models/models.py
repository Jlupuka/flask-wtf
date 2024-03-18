import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import ForeignKey, Table, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db_session import SqlAlchemyBase

job_to_category = Table(
    'job_to_category',
    SqlAlchemyBase.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
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

    jobs: Mapped[list['Jobs']] = relationship(back_populates='user', uselist=True)
    department: Mapped['Department'] = relationship(back_populates='user')
    categories: Mapped[list['Category']] = relationship(back_populates='user', uselist=True)

    def __repr__(self) -> str:
        return f'<Colonist> {self.id} {self.name} {self.surname}'

    def set_password(self, password: str) -> None:
        self.hashed_password: str = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.hashed_password, password)


class Jobs(SqlAlchemyBase, UserMixin, SerializerMixin):
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
    category: Mapped['Category'] = relationship(secondary=job_to_category,
                                                back_populates='jobs',
                                                overlaps='jobs')


class Department(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'departments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[Optional[str]]
    chief: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    members: Mapped[Optional[str]]
    email: Mapped[Optional[str]]

    user: Mapped['User'] = relationship(back_populates='department')


class Category(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['User'] = relationship(back_populates="categories")
    jobs: Mapped[list['Jobs']] = relationship(secondary=job_to_category,
                                              back_populates='category')
