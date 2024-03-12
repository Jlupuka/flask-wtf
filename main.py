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

    return render_template(template_name_or_list='training.html', title=typeMission,
                           prof=prof, imageName=image_dict[typeMission],
                           typeMission=typeMission)


@app.route('/list_prof/<typeList>')
def list_prof(typeList: str) -> str:
    professionList = {"Инженер по разработке систем жизнеобеспечения",
                      "Геолог-исследователь",
                      "Инженер по строительству и инфраструктуре",
                      "Психолог",
                      "Aгроном/ботаник",
                      "Учёный-биолог",
                      "Химик-исследователь ресурсов",
                      "Астрофизик",
                      "Лётчик",
                      "Инженер-робототехник",
                      "Архитектор-дизайнер",
                      "Специалист по энергетическим системам",
                      "Медицинский специалист",
                      "Учёный по терраформированию",
                      "Инженер-космонавигатор",
                      "Специалист по защите от радиации",
                      "Специалист по водородному исследованию",
                      "Инженер-рециклер",
                      "Лингвист",
                      "Управляющий колонией"}
    return render_template(template_name_or_list='workers.html', typeList=typeList,
                           professionList=professionList)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
