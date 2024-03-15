from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, regexp


class JobForm(FlaskForm):
    teamleader = IntegerField('ID Team Leader', validators=[DataRequired()])
    job = StringField('Наименование работы', validators=[DataRequired()])
    work_size = IntegerField('Дедлайн', validators=[DataRequired()])
    collaborators = StringField('ID работника(-ов)', validators=[DataRequired(),
                                                                 regexp(r'^\s*\d+(\s*,\s*\d+)*\s*$')])
    is_job_finished = BooleanField('Is job finished?')
    submit = SubmitField('Добавить')
