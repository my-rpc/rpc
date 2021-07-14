from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, Email, ValidationError

from rpc_package.rpc_tables import Provinces, District, User_roles, Employees
from rpc_package.utils import check_language


class CreateUserForm(FlaskForm):
    role_list = [(role.id, role.name_english) for role in User_roles.query.all()]
    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 8', min=7, max=7),
                                                         Regexp('RPC-\d+', message='Invalid employee ID.')])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_role = SelectField('Provinces', choices=role_list, validators=[DataRequired()])

    submit = SubmitField('Create New User')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    prefer_language = RadioField('Language', choices=[('dari', 'Dari'), ('en', 'English')], default='en')
    submit = SubmitField('Login')


class EmployeeForm(FlaskForm):
    emp_id = [emp.id for emp in Employees.query.all()]
    emp_id.sort()
    if len(emp_id) > 0:
        last_emp_id = emp_id[-1]
    else:
        last_emp_id = 'RPC-001'

    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 7', min=7,
                                                        max=7), Regexp('RPC-\d+', message='Invalid employee ID.')],
                                                        default=last_emp_id)

    first_name = StringField('نام', validators=[DataRequired()])
    last_name = StringField('تخلص', validators=[DataRequired()])
    father_name = StringField('نام پدر', validators=[DataRequired()])
    grand_name = StringField('نام پدر کلان', validators=[DataRequired()])

    first_name_english = StringField('First Name')
    last_name_english = StringField('Last Name')
    father_name_english = StringField('Father Name')
    grand_name_english = StringField('Grand Father Name')

    # TODO adding datetime picker.
    birthday = StringField('Birthday')
    tazkira = StringField('Tazkira', validators=[Regexp('\d+')])
    gender = RadioField('Gender', choices=[(1, 'Male'), (0, 'Female')], validators=[DataRequired()])
    blood = StringField("Blood Type", validators=[Regexp('(A|B|AB|O|C)[+-]')], default='C+')
    m_status = RadioField('Marital Status', choices=[(1, 'Married'), (0, 'Single')], validators=[DataRequired()])
    tin = StringField('TIN Number', validators=[Regexp('\d+')], default='000')
    provinces_list = [(province.id, province.province_name) for province in Provinces.query.all()]
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    permanent_address = StringField('Permanent Address', validators=[DataRequired()])
    current_address = StringField('Current Address', validators=[DataRequired()])
    provinces = SelectField('Provinces', choices=provinces_list, validators=[DataRequired()])
    district = SelectField('District', validators=[])

    submit = SubmitField('Add Employee')

    def validate_first_name(self, first_name):
        if not check_language(first_name.data):
            raise ValidationError("نام باید به دری نوشته شود.")

    def validate_last_name(self, last_name):
        if not check_language(last_name.data):
            raise ValidationError("تخلص باید به دری نوشته شود.")

    def validate_father_name(self, father_name):
        if not check_language(father_name.data):
            raise ValidationError("نام پدر باید به دری نوشته شود.")

    def validate_grand_name(self, grand_name):
        if not check_language(grand_name.data):
            raise ValidationError("نام پدرکلان باید به دری نوشته شود.")




