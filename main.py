import json
import os

from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

from loginform import LoginForm
from models.models import FlaskData
from services.service import Service

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/index')
def index() -> str:
    title = "Миссия Колонизация Марса"
    return render_template('base.html', title=title)


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
        return redirect('/index')
    return render_template(template_name_or_list='login.html', title='Авторизация', form=form)


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


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png']


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
