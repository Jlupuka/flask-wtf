import flask
from flask import jsonify, make_response, abort, request

from data import db_session
from data.models.models import Jobs, Category

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_jobs() -> dict[str: list]:
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('id', 'team_leader', 'job',
                                    'work_size', 'collaborators', 'start_date',
                                    'end_date', 'is_finished'))
                 for item in jobs
                 ]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>')
def get_one_job(job_id: int) -> dict[str: list]:
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        abort(400)
    return jsonify(
        {
            'jobs': job.to_dict(only=(
                'id', 'team_leader', 'job',
                'work_size', 'collaborators', 'start_date',
                'end_date', 'is_finished'))

        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}, 400))
    elif not all(key in request.json for key in (
                'team_leader', 'job', 'id_category',
                'work_size', 'collaborators', 'is_finished')):
        abort(400)
    db_sess = db_session.create_session()
    category_obj = db_sess.query(Category).filter(Category.id == request.json['id_category']).first()
    if not category_obj:
        return make_response(jsonify({'error': 'Not found this id_category'}, 400))
    job = Jobs()
    job.job = request.json['job']
    job.team_leader = request.json['team_leader']
    job.work_size = request.json['work_size']
    job.collaborators = request.json['collaborators']
    job.is_finished = request.json['is_finished']
    job.category = category_obj
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'id': job.id})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id: int) -> dict[str: str]:
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
        return jsonify({'success': 'OK'})
    else:
        abort(404)


@blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id: int) -> dict[str: str]:
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        for key, value in request.json.items():
            if hasattr(job, key):
                setattr(job, key, value)
            else:
                abort(404)
        db_sess.commit()
        return jsonify({'success': 'OK'})
    abort(404)
