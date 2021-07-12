from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email

from rpc_package.rpc_tables import Provinces, District, User_roles


class CreateUserForm(FlaskForm):
    role_list = [(role.id, role.name_english) for role in User_roles.query.all()]
    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 8', min=7, max=7),
                                                         Regexp('RPC-\d+', message='Invalid employee ID.')])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # TODO add the foreign key of the role table.
    user_role = SelectField('Provinces', choices=role_list, validators=[DataRequired()])

    submit = SubmitField('Create New User')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    prefer_language = RadioField('Language', choices=[('dari', 'Dari'), ('en', 'English')], default='en')
    submit = SubmitField('Login')


class EmployeeForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 8', min=7,
                                                                max=7),
                                                         Regexp('RPC-\d+', message='Invalid employee ID.')])

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    father_name = StringField('Father Name', validators=[DataRequired()])
    grand_name = StringField('Grand Father Name', validators=[DataRequired()])

    first_name_english = StringField('First Name')
    last_name_english = StringField('Last Name')
    father_name_english = StringField('Father Name')
    grand_name_english = StringField('Grand Father Name')

    # TODO adding datetime picker.
    birthday = StringField('Birthday')
    tazkira = StringField('Tazkira', validators=[Regexp('\d+')])
    gender = RadioField('Gender', choices=[(1, 'Male'), (0, 'Female')], validators=[DataRequired()])
    blood = StringField("Blood Type", validators=[Regexp('(A|B|AB|O)[+-]')])
    m_status = RadioField('Marital Status', choices=[(1, 'Married'), (0, 'Single')], validators=[DataRequired()])
    tin = StringField('TIN Number', validators=[Regexp('\d+')])

    submit = SubmitField('Save and Next')


class EmployeeContactForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    provinces_list = [(province.id, province.province_name) for province in Provinces.query.all()]
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Email Address', validators=[DataRequired(), Email()])
    permanent_address = StringField('Permanent Address', validators=[DataRequired()])
    current_address = StringField('Current Address', validators=[DataRequired()])
    provinces = SelectField('Provinces', choices=provinces_list, validators=[DataRequired()])
    district = SelectField('District', validators=[DataRequired()])

    submit = SubmitField('Add Employee')






