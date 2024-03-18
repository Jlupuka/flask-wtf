import datetime

from flask import jsonify
from flask_restful import Resource

from data import db_session
from data.models.models import User
from parsers import Parsers


class UsersResource(Resource):
    def get(self, user_id: int) -> dict[str: str]:
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        return jsonify(
            {
                'user': user.to_dict(only=(
                    'id', 'surname', 'name',
                    'age', 'position', 'speciality',
                    'address', 'email', 'modified_date'))

            }
        )

    def put(self, user_id: int) -> dict[str: str]:
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        args = Parsers.users_parser(required=False).parse_args()
        for key, values in args.items():
            if values:
                setattr(user, key, values)
        user.modified_date = datetime.datetime.now(datetime.UTC)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user_id: int) -> dict[str: str]:
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self) -> dict[str: list[dict[str: str]]]:
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=('id', 'surname', 'name'))
                     for item in users
                     ]
            }
        )

    def post(self) -> dict[str: str]:
        session = db_session.create_session()
        args = Parsers.users_parser(required=True).parse_args()
        user = User()
        for key, value in args.items():
            if key != 'password':
                setattr(user, key, value)
        user.set_password(password=args['password'])
        user.modified_date = datetime.datetime.now(datetime.UTC)
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
