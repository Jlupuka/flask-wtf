import datetime
import json
import os
from typing import Type

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, make_response, session, abort

from werkzeug import Response
from werkzeug.utils import secure_filename

from data import db_session
from data.models.models import Jobs, User, Department
from forms.departmentForm import DepartmentForm
from forms.jobForm import JobForm
from forms.loginform import LoginForm
from models.models import FlaskData
from forms.regform import RegisterForm
from services.service import Service

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)


@login_manager.user_loader
def load_user(user_id: int) -> Type[User]:
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).one()
    return user


@app.route('/')
@app.route('/index')
def index() -> str:
    title = "Миссия Колонизация Марса"
    if login_user:
        return render_template('works_log.html', title=title,
                               jobs_data=session_db.query(Jobs).all())
    return render_template('base.html', title=title)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/training/<prof>')
def training(prof: str) -> str:
    image_dict: dict[str: str] = {
        'Научные симуляторы': 'med.png',
        'Инженерные тренажеры': 'engineer.png'
    }
    typeMission = 'Научные симуляторы'
    if prof.lower() in {'инженер', 'строитель'}:
        typeMission = 'Инженерные тренажеры'

    return render_template(template_name_or_list='training.html', title=typeMission,
                           prof=prof, imageName=image_dict[typeMission],
                           typeMission=typeMission)


@app.route('/list_prof/<typeList>')
def list_prof(typeList: str) -> str:
    return render_template(template_name_or_list='workers.html', typeList=typeList,
                           professionList=FlaskData.professionList.value)


@app.route('/answer', methods=['POST', 'GET'])
def answer() -> str:
    if request.method == 'GET':
        return render_template(template_name_or_list='answer.html', professionList=FlaskData.professionList.value,
                               title=FlaskData.formTitle.value)
    if request.method == 'POST':
        result_dict = {
            'profession': [],
            'ready': False
        }
        for key, data in request.values.items():
            if data == 'on' and key != 'ready':
                result_dict['profession'].append(key)
            else:
                result_dict[key] = data
        result_dict['profession'] = ', '.join(result_dict['profession'])
        result_dict['ready'] = True if result_dict['ready'] == 'on' else False
        return render_template(template_name_or_list='auto_answer.html', **result_dict)


@app.route('/auto_answer')
def auto_answer() -> str:
    return render_template(template_name_or_list='auto_answer.html', **FlaskData.auto_answer.value)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    if request.method == 'POST':
        return render_template('login.html', title='Авторизация', form=form,
                               message='Некорректно введены поля авторизации')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/distribution')
def distribution() -> str:
    return render_template(template_name_or_list='distribution.html', title='По каютам!',
                           distributions=FlaskData.distribution.value)


@app.route('/table/<gender>/<int:age>', methods=['GET'])
def table(gender: str, age: int) -> str:
    if gender == 'male':
        wall_color = 'blue'
    elif gender == 'female':
        wall_color = 'pink'
    else:
        return 'Invalid gender'
    marsian_image = 'marsOld.png' if age > 21 else 'marsYang.png'
    return render_template('table.html', wall_color=wall_color, marsian_image=marsian_image)


@app.route('/gallery', methods=['POST', 'GET'])
def gallery() -> str:
    if request.method == 'POST':
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join('static/images/mars_image', filename))
            return render_template('gallery.html', fileNames=Service.get_filenames_mars_img())
    return render_template('gallery.html', fileNames=Service.get_filenames_mars_img())


@app.route('/member')
def member() -> str:
    with open('templates/data.json', encoding='utf-8', mode='r') as file:
        data = json.load(file)
    return render_template('member.html', title='Личная карточка',
                           data=data['data'])


@app.route('/registration', methods=['GET', 'POST'])
def registration() -> Response | str:
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.surname = form.surname.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route("/addjob", methods=['GET', 'POST'])
@login_required
def add_job() -> str | Response:
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Jobs).filter(Jobs.job == form.job.data).first():
            return render_template('add_job.html', title='Добавление работы',
                                   form=form,
                                   message="Такие данные уже есть")
        if not db_sess.query(User).filter(User.id == form.teamleader.data).first():
            return render_template('add_job.html', title='Добавление работы',
                                   form=form,
                                   message=f"Team Leader'а с такими ID ({form.teamleader.data}) - нет")

        job = Jobs()
        job.job = form.job.data
        job.team_leader = form.teamleader.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_job_finished.data
        current_user.job.append(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Добавление работы', form=form)


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def update_job(id: int) -> str | Response:
    form = JobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id != 1:
            job: Type[Jobs] = db_sess.query(Jobs).filter(Jobs.id == id,
                                                         Jobs.team_leader == current_user.id
                                                         ).first()
        else:
            job: Type[Jobs] = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if job:
            form.teamleader.data = job.team_leader
            form.job.data = job.job
            form.work_size.data = job.work_size
            form.is_job_finished.data = job.is_finished
            form.collaborators.data = job.collaborators
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(User).filter(User.id == form.teamleader.data).first():
            return render_template('add_job.html', title='Обновление работы',
                                   form=form,
                                   message=f"Team Leader'а с такими ID ({form.teamleader.data}) - нет")
        if current_user.id != 1:
            job: Type[Jobs] = db_sess.query(Jobs).filter(Jobs.id == id,
                                                         Jobs.team_leader == current_user.id
                                                         ).first()
        else:
            job: Type[Jobs] = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if job:
            job.job = form.job.data
            job.team_leader = form.teamleader.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_job_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html', title='Обновление работы', form=form)


@app.route('/job_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id: int) -> Response:
    db_sess = db_session.create_session()
    if current_user.id != 1:
        job: Type[Jobs] = db_sess.query(Jobs).filter(Jobs.id == id,
                                                     Jobs.team_leader == current_user.id
                                                     ).first()
    else:
        job: Type[Jobs] = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/department')
@login_required
def department() -> str:
    return render_template('department.html', title='Департамент',
                           department_data=session_db.query(Department).all())


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department() -> str | Response:
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Department).filter(Department.title == form.title.data).first():
            return render_template('add_department.html', title='Добавление департамента',
                                   form=form,
                                   message="Такие данные уже есть")
        if not db_sess.query(User).filter(User.id == form.chief.data).first():
            return render_template('add_department.html', title='Добавление департамента',
                                   form=form,
                                   message=f"Team Leader'а с такими ID ({form.chief.data}) - нет")
        department_obj = Department()
        department_obj.title = form.title.data
        department_obj.chief = form.chief.data
        department_obj.members = form.members.data
        department_obj.email = form.email.data
        current_user.department = department_obj
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/department')
    return render_template('add_department.html', title='Добавление департамента', form=form)


@app.route('/department/<int:id>', methods=['GET', 'POST'])
@login_required
def update_department(id: int) -> str | Response:
    form = DepartmentForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id != 1:
            department_obj: Type[Department] | None = (db_sess.query(Department)
                                                       .filter(Department.id == id,
                                                               Department.chief == current_user.id
                                                               ).first())
        else:
            department_obj: Type[Department] | None = (db_sess.query(Department)
                                                       .filter(Department.id == id).first())
        if department_obj:
            form.title.data = department_obj.title
            form.members.data = department_obj.members
            form.members.data = department_obj.members
            form.email.data = department_obj.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(User).filter(User.id == form.chief.data).first():
            return render_template('add_department.html', title='Обновление Департамент',
                                   form=form,
                                   message=f"Team Leader'а с такими ID ({form.chief.data}) - нет")
        if current_user.id != 1:
            department_obj: Type[Department] | None = (db_sess.query(Department)
                                                       .filter(Department.id == id,
                                                               Department.chief == current_user.id
                                                               ).first())
        else:
            department_obj: Type[Department] | None = (db_sess.query(Department)
                                                       .filter(Department.id == id).first())
        if department_obj:
            department_obj.title = form.title.data
            department_obj.members = form.members.data
            department_obj.members = form.members.data
            department_obj.email = form.email.data
            db_sess.commit()
            return redirect('/department')
        else:
            abort(404)
    return render_template('add_department.html', title='Обновление Департамента', form=form)


@app.route('/department_delete/<int:id>')
@login_required
def department_delete(id: int) -> Response:
    db_sess = db_session.create_session()
    if current_user.id != 1:
        department_obj: Type[Department] | None = (db_sess.query(Department)
                                                   .filter(Department.id == id,
                                                           Department.chief == current_user.id
                                                           ).first())
    else:
        department_obj: Type[Department] | None = (db_sess.query(Department)
                                                   .filter(Department.id == id).first())
    if department_obj:
        db_sess.delete(department_obj)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/department')


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png']


if __name__ == '__main__':
    db_session.global_init('db/workers.sqlite')
    session_db = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')
