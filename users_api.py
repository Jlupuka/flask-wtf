import datetime

import flask
from flask import jsonify, make_response, abort, request

from data import db_session
from data.models.models import User

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_jobs() -> dict[str: list]:
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'surname', 'name'))
                 for item in users
                 ]
        }
    )


@blueprint.route('/api/users/<int:user_id>')
def get_one_job(user_id: int) -> dict[str: list]:
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user:
        abort(400)
    return jsonify(
        {
            'user': user.to_dict(only=(
                'id', 'surname', 'name',
                'age', 'position', 'speciality',
                'address', 'email', 'modified_date'))

        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_job():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    elif all(key in request.json for key in (
                'surname', 'name',
                'age', 'position', 'speciality',
                'address', 'email', 'password')):
        abort(400)
    db_sess = db_session.create_session()
    user = User()
    user.name = request.json['name']
    user.email = request.json['email']
    user.surname = request.json['surname']
    user.age = request.json['age']
    user.position = request.json['position']
    user.speciality = request.json['speciality']
    user.address = request.json['address']
    user.modified_date = datetime.datetime.now(datetime.UTC)
    user.set_password(request.json['password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'id': user.id})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_job(user_id: int) -> dict[str: str]:
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})
    else:
        abort(404)


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def update_job(user_id: int) -> dict[str: str]:
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in request.json.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                abort(404)
        user.modified_date = datetime.datetime.now(datetime.UTC)
        db_sess.commit()
        return jsonify({'success': 'OK'})
    abort(404)
