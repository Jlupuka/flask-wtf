from flask import jsonify, make_response
from flask_restful import Resource
from sqlalchemy.orm import Session

from data import db_session
from data.models.models import Jobs, Category
from parsers import Parsers


class JobsResource(Resource):
    def get(self, job_id: int) -> dict[str: str]:
        session: Session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        return jsonify(
            {
                'job': job.to_dict(only=(
                    'id', 'team_leader', 'job',
                    'work_size', 'collaborators', 'start_date',
                    'end_date', 'is_finished'))

            }
        )

    def put(self, job_id: int) -> dict[str: str]:
        session: Session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        args = Parsers.users_parser(required=False).parse_args()
        for key, values in args.items():
            if values:
                setattr(job, key, values)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, job_id: int) -> dict[str: str]:
        session: Session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self) -> dict[str: list[dict[str: str]]]:
        session: Session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify(
            {
                'jobs':
                    [item.to_dict(only=('id', 'team_leader', 'job'))
                     for item in jobs
                     ]
            }
        )

    def post(self) -> dict[str: str]:
        session: Session = db_session.create_session()
        args = Parsers.jobs_parser(required=True).parse_args()
        category_obj = session.query(Category).filter(Category.id == args['id_category']).first()
        if not category_obj:
            return make_response(jsonify({'error': 'Not found this id_category'}, 400))
        job = Jobs()
        for key, value in args.items():
            setattr(job, key, value)
        job.category = category_obj
        session.add(job)
        session.commit()
        return jsonify({'id': job.id})
