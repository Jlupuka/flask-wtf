from typing import Iterable, Any

from flask import Flask
from sqlalchemy.orm import Session
from werkzeug.wrappers import Request


from data import db_session
from data.models.models import User
from exceptions.castomException import UserExceptions


class Middleware:
    def __init__(self, app: Flask) -> None:
        self.app = app

    def __call__(self, environ: Any, start_response: Any) -> Iterable[bytes]:
        request: Request = Request(environ)
        if len((data := request.path.split('/v2/users/'))) > 1:
            session: Session = db_session.create_session()
            user: User | None = session.query(User).get(data[1])
            if not user:
                return UserExceptions.user_not_found(user_id=data[1], start_response=start_response)
        return self.app(environ, start_response)
