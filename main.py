import datetime
import json
import os
from typing import Type

import requests
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, make_response, session, abort, jsonify

from werkzeug import Response
from werkzeug.utils import secure_filename

import jobs_api
import users_api
from data import db_session
from data.models.models import Jobs, User, Department, Category
from forms.categoryForm import CategoryForm
from forms.departmentForm import DepartmentForm
from forms.jobForm import JobForm
from forms.loginform import LoginForm
from models.models import FlaskData
from forms.regform import RegisterForm
from service.service import YandexMapAPI
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


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


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
        if user and user.check_password(password=form.password.data):
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
        user.modified_date = datetime.datetime.now(datetime.UTC)
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
        category_obj = db_sess.query(Category).filter(Category.id == form.id_category.data).first()
        if db_sess.query(Jobs).filter(Jobs.job == form.job.data).first():
            return render_template('add_job.html', title='Добавление работы',
                                   form=form,
                                   message="Такие данные уже есть")
        if not db_sess.query(User).filter(User.id == form.teamleader.data).first():
            return render_template('add_job.html', title='Добавление работы',
                                   form=form,
                                   message=f"Team Leader'а с такими ID ({form.teamleader.data}) - нет")
        if not category_obj:
            return render_template('add_job.html', title='Обновление работы',
                                   form=form,
                                   message=f"Категории с таким ID ({form.teamleader.data}) - нет")

        job = Jobs()
        job.job = form.job.data
        job.team_leader = form.teamleader.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_job_finished.data
        job.category = category_obj
        # current_user.jobs.append(job)
        db_sess.merge(job)
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
            form.id_category.data = job.category.id
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        category_obj = db_sess.query(Category).filter(Category.id == form.id_category.data).first()
        if not db_sess.query(User).filter(User.id == form.teamleader.data).first():
            return render_template('add_job.html', title='Обновление работы',
                                   form=form,
                                   message=f"Team Leader'а с такими ID ({form.teamleader.data}) - нет")
        if not category_obj:
            return render_template('add_job.html', title='Обновление работы',
                                   form=form,
                                   message=f"Категории с таким ID ({form.teamleader.data}) - нет")
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
            job.category = category_obj
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


@app.route('/category')
@login_required
def category() -> str:
    return render_template('category.html', title='Категории',
                           category_data=session_db.query(Category).all())


@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category() -> str | Response:
    form = CategoryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Department).filter(Department.title == form.name.data).first():
            return render_template('add_category.html', title='Добавление категории',
                                   form=form,
                                   message="Такие данные уже есть")
        category_obj = Category()
        category_obj.name = form.name.data
        category_obj.user_id = category_obj.id
        current_user.categories.append(category_obj)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/category')
    return render_template('add_category.html', title='Добавление категории', form=form)


@app.route('/category/<int:id>', methods=['GET', 'POST'])
@login_required
def update_category(id: int) -> str | Response:
    form = CategoryForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id != 1:
            category_obj: Type[Category] | None = (db_sess.query(Category)
                                                   .filter(Category.id == id,
                                                           Category.user_id == current_user.id
                                                           ).first())
        else:
            category_obj: Type[Category] | None = (db_sess.query(Category)
                                                   .filter(Category.id == id).first())
        if category_obj:
            form.name.data = category_obj.name
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.id != 1:
            category_obj: Type[Category] | None = (db_sess.query(Category)
                                                   .filter(Category.id == id,
                                                           Category.user_id == current_user.id
                                                           ).first())
        else:
            category_obj: Type[Category] | None = (db_sess.query(Category)
                                                   .filter(Category.id == id).first())
        if category_obj:
            category_obj.name = form.name.data
            db_sess.commit()
            return redirect('/category')
        else:
            abort(404)
    return render_template('add_category.html', title='Обновление Категории', form=form)


@app.route('/category_delete/<int:id>')
@login_required
def category_delete(id: int) -> Response:
    db_sess = db_session.create_session()
    if current_user.id != 1:
        category_obj: Type[Category] | None = (db_sess.query(Category)
                                               .filter(Category.id == id,
                                                       Category.user_id == current_user.id
                                                       ).first())
    else:
        category_obj: Type[Category] | None = (db_sess.query(Category)
                                               .filter(Category.id == id).first())
    if category_obj:
        db_sess.delete(category_obj)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/category')


@app.route('/user_show/<int:user_id>')
def show_user(user_id: int) -> str:
    api_url = 'http://127.0.0.1:8080/api/users'
    user_data = requests.get(url=api_url + f'/{user_id}').json()['user']
    if user_data.get('error') is not None:
        return render_template('show_user.html',
                               errorMessage=f'Not found user ({user_id})')
    link_photo: dict | str = YandexMapAPI().link_photo_city(cityName=user_data['address'])
    if isinstance(link_photo, type(dict)):
        return render_template('show_user.html',
                               errorMessage=f'Not found place ({user_data['address']})')
    return render_template('show_user.html', name=user_data['name'],
                           surname=user_data['surname'], cityPhotoLink=link_photo,
                           city=user_data['address'])


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
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
