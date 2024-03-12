from flask import Flask, render_template, request
from models.models import FlaskData

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
