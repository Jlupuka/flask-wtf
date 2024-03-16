from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class CategoryForm(FlaskForm):
    name = StringField('Наименование категории', validators=[DataRequired()])
    submit = SubmitField('Добавить')
