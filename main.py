from flask import Flask, render_template

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

    return render_template('training.html', prof=prof, imageName=image_dict[typeMission],
                           typeMission=typeMission)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
