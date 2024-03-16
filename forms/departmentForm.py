from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, EmailField
from wtforms.validators import DataRequired, regexp


class DepartmentForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    chief = IntegerField('ID Leader', validators=[DataRequired()])
    members = StringField('ID работника(-ов)', validators=[DataRequired(),
                                                           regexp(r'^\s*\d+(\s*,\s*\d+)*\s*$')])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Добавить')
