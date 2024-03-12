from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    idAstronaut = IntegerField('Id астронавта', validators=[DataRequired()])
    passwordAstronaut = PasswordField('Пароль астронавта', validators=[DataRequired()])
    idCapitan = IntegerField('Id капитана', validators=[DataRequired()])
    passwordCapitan = StringField('Токен капитана', validators=[DataRequired()])
    submit = SubmitField('Доступ')
