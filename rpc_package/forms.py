from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp


class CreateUserForm(FlaskForm):
    # TODO add the foreign key of the employee table.
    # TODO fine the special character validator.
    employee_id = StringField('Employee ID', validators=[DataRequired(),
                                                         Length(min=6, max=20),
                                                         Regexp('RPC_\d+', message='Invalid employee ID.')])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # TODO add the foreign key of the role table.
    user_role = StringField("User Role", validators=[DataRequired()])

    submit = SubmitField('Create New User')


class LoginForm(FlaskForm):
    # TODO add the foreign key of the employee table.
    employee_id = StringField('Employee ID', validators=[DataRequired(),
                                                         Length(min=6, max=20)])

    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')