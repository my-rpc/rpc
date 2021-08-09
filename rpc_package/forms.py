from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, HiddenField, SubmitField, BooleanField, RadioField, SelectField, \
    FileField, DecimalField, DateField, TimeField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError
import re
from rpc_package.rpc_tables import Provinces, Districts, User_roles, Employees, Emails, Phone
from rpc_package.utils import check_language


class CreateUserForm(FlaskForm):
    role_list = [(role.id, role.name_english) for role in User_roles.query.all()]
    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 8', min=7,
                                                                max=7),
                                                         Regexp('RPC-\d+', message='Invalid employee ID.')])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_role = SelectField('Provinces', choices=role_list, validators=[DataRequired()])

    submit = SubmitField('Create New User')


class UpdateUserForm(FlaskForm):
    role_list = [(role.id, role.name_english) for role in User_roles.query.all()]
    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 7', min=7,
                                                                max=7),
                                                         Regexp('RPC-\d+', message='Invalid employee ID.')])
    user_role = SelectField('User Role', choices=role_list, validators=[DataRequired()])
    submit = SubmitField('Update User Role')


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
        # print(last_emp_id[4:])
    else:
        last_emp_id = 'RPC-001'

    employee_id = StringField('Employee ID', validators=[DataRequired(message='Employee ID is required!'),
                                                         Length(message='Employee ID length must be at least 7', min=7,
                                                                max=7),
                                                         Regexp('RPC-\d+', message='Invalid employee ID.')],
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
    birthday = StringField('Birthday/تارخ تولد')
    tazkira = StringField('Tazkira/تذکره', validators=[Regexp('\d+')])
    gender = RadioField('Gender', choices=[[1, 'Male'], [0, 'Female']], validators=[DataRequired()])
    blood = StringField("Blood Type/گروپ خون", validators=[Regexp('(A|B|AB|O|C)[+-]')], default='C+')
    m_status = RadioField('Marital Status', choices=[[1, 'Married'], [0, 'Single']], validators=[DataRequired()])
    tin = StringField('TIN Number/نمبر تشخصیه', validators=[Regexp('\d+')], default='000')
    provinces_list = [(province.id, province.province_name + '/' + province.province_name_english) for province in
                      Provinces.query.all()]
    districts_list = [(district.id, district.district_name + '/' + district.district_name_english) for district in
                      Districts.query.all()]
    email = StringField('Email Address')
    email_second = StringField('Email Address')
    phone = StringField('Phone Address', validators=[DataRequired()])
    phone_second = StringField('Second Phone Address')
    permanent_address = StringField('Permanent Address/سکونت اصلی', validators=[DataRequired()])
    permanent_address_dari = StringField('Permanent Address/سکونت اصلی', validators=[DataRequired()])
    current_address = StringField('Current Address/سکونت فعلی', validators=[DataRequired()])
    current_address_dari = StringField('Current Address/سکونت فعلی', validators=[DataRequired()])
    provinces_permanent = SelectField('Provinces', choices=provinces_list, validators=[DataRequired()])
    provinces_current = SelectField('Provinces', choices=provinces_list, validators=[DataRequired()])
    district_permanent = SelectField('Districts', validators=[DataRequired()], choices=districts_list)
    district_current = SelectField('Districts', validators=[DataRequired()], choices=districts_list)
    submit = SubmitField('Add Employee')

    def validate_email(self, email):
        if email.data:
            if not bool(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email.data)):
                raise ValidationError('فرمت ایمیل را چک کنید')
            user_email = Emails.query.filter_by(email=email.data).first()
            if user_email:
                raise ValidationError('ایمیل شما موجود است')

    def validate_email_second(self, email_second):
        if email_second.data:
            if not email_second.data:
                if not bool(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_second.data)):
                    raise ValidationError('فرمت ایمیل را چک کنید')
            user_email = Emails.query.filter_by(email=email_second.data).first()
            if user_email:
                raise ValidationError('ایمیل شما موجود است')

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

    def validate_phone(self, phone):
        if not bool(
                re.match(r'(\d{3}[-\.\s]*\d{3}[-\.\s]*\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})',
                         phone.data)):
            raise ValidationError("فرمت شماره تماس خود را چک کنید 0875.231.1235 ")
        user_phone = Phone.query.filter_by(phone=phone.data).first()
        if user_phone:
            raise ValidationError('تلفون شما موجود است')

    def validate_phone_second(self, phone_second):
        if phone_second.data != '':
            if not bool(
                    re.match(r'(\d{3}[-\.\s]*\d{3}[-\.\s]*\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})',
                             phone_second.data)):
                raise ValidationError("فرمت شماره تماس خود را چک کنید 0875.231.1235 ")
        user_phone = Phone.query.filter_by(phone=phone_second.data).first()
        if user_phone:
            raise ValidationError('تلفون شما موجود است')

    def validate_employee_id(self, employee_id):
        employee = Employees.query.get(employee_id.data)
        if employee:
            raise ValidationError('Employee already exist, please check your employee ID')

    def validate_birthday(self, birthday):
        if birthday.data:
            if not bool(re.match(r'1\d{3}[-\\](0[1-9]|1[0-2])[-\\](0[1-9]|1[0-9]|2[0-9]|3[0-1])', birthday.data)):
                raise ValidationError('Date format is incorrect yyyy-mm-dd')


class UploadCVForm(FlaskForm):
    cv = FileField('CV File', validators=[DataRequired(), Regexp("\w+\.pdf$")])
    flag = HiddenField('flag', default="cv")
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])


class UploadGuarantorForm(FlaskForm):
    guarantor = FileField('Guarantor File', validators=[DataRequired(), Regexp("\w+\.pdf$")])
    flag = HiddenField('flag', default="guarantor")
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])


class UploadEducationalDocsForm(FlaskForm):
    education = FileField('Education File', validators=[DataRequired(), Regexp("\w+\.pdf$")])
    flag = HiddenField('flag', default="education")
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])


class UploadTinForm(FlaskForm):
    tin = FileField('Tin File', validators=[DataRequired(), Regexp("\w+\.pdf$")])
    flag = HiddenField('flag', default="tin")
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])


class UploadTazkiraForm(FlaskForm):
    tazkira = FileField('Tazkira File', validators=[DataRequired(), Regexp("\w+\.pdf$")])
    flag = HiddenField('flag', default="tazkira")
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])


class UploadExtraDocsForm(FlaskForm):
    extra_docs = FileField('extra Document Files', validators=[DataRequired(), Regexp("\w+\.pdf$")])
    flag = HiddenField('flag', default="extra_docs")
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])

class leaveRequestForm(FlaskForm):
    leave_type = RadioField('Leave Type', default=1, choices=[[1, 'Hourly'], [0, 'Daily']], validators=[DataRequired()])
    start_datetime = DateTimeField('From', validators=[DataRequired()])
    end_datetime = DateTimeField('To', validators=[DataRequired()])
    submit = SubmitField('Send Request')
    
class ResignRequestForm(FlaskForm):
    reason = StringField(u'Reason', widget=TextArea(),validators=[DataRequired()])
    responsibilities = StringField(u'Responsibilities', widget=TextArea(),validators=[DataRequired()])
    equipments = StringField(u'Equipments', widget=TextArea(),validators=[DataRequired()])
    submit = SubmitField('Send Request')
    