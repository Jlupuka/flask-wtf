from typing import Iterable, Any

from flask import Flask
from sqlalchemy.orm import Session
from werkzeug.wrappers import Request

from data import db_session
from data.models.models import User, Jobs
from exceptions.castomException import Exceptions


class Middleware:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def __call__(self, environ: Any, start_response: Any) -> Iterable[bytes]:
        request: Request = Request(environ)
        if len((data := request.path.split('/v2/'))) > 1:
            data_id = data[1].split('/')
            if len(data_id) > 1:
                session: Session = db_session.create_session()
                if 'users' in data[1]:
                    user: User | None = session.query(User).get(data_id[1])
                    if not user:
                        return Exceptions.user_not_found(user_id=data_id[1], start_response=start_response)
                else:
                    job: Jobs | None = session.query(Jobs).get(data_id[1])
                    if not job:
                        return Exceptions.job_not_found(job_id=data_id[1], start_response=start_response)
        return self.app(environ, start_response)
