from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, HiddenField, SubmitField, BooleanField, RadioField, \
     DecimalField, DateField, TimeField, IntegerField, SelectField, FileField,  TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError, AnyOf
import re
from wtforms.widgets import TextArea
from rpc_package.rpc_tables import Provinces, Districts, User_roles, Employees, Emails, Phone, Contract_types, \
    Positions, Departments, Salary
from rpc_package.utils import check_language, datetime_validation, date_validation
from rpc_package import translation_obj, message_obj
import jdatetime, datetime

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
    gender = RadioField('Gender', choices=[[1, 'Male'], [0, 'Female']], validators=[DataRequired(), AnyOf(values=["1", "0"])])
    blood = StringField("Blood Type/گروپ خون", validators=[Regexp('(A|B|AB|O|C)[+-]')], default='C+')
    m_status = RadioField('Marital Status', choices=[[1, 'Married'], [0, 'Single']], validators=[DataRequired(), AnyOf(values=["1", "0"])])
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

    def __init__(self):
        super(EmployeeForm,self).__init__()
        self.language = 'dari'

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
        if not birthday.data:
            raise ValidationError(message_obj.required_field[self.language].replace('{}', translation_obj.birthday[self.language] + ' '))
        elif not date_validation(self, birthday.data):
            raise ValidationError(message_obj.incorrect_date_format[self.language])
        # value = jdatetime.datetime.strptime(birthday.data, '%Y-%m-%d')
        # birthday.data = value.togregorian()


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


class ContractForm(FlaskForm):
    # options = [('', '------')]
    contract_type_list = [(con_type.id, con_type.name_english + ' / ' + con_type.name) for con_type in
                          Contract_types.query.all()]
    position_list = [(position.id, position.name_english + ' / ' + position.name) for position in Positions.query.all()]
    department_list = [(department.id, department.name_english + ' / ' + department.name) for department in
                       Departments.query.all()]
    contract_type_list.insert(0, ('', '------'))
    position_list.insert(0, ('', '------'))
    department_list.insert(0, ('', '------'))
    contract_type = SelectField('Contract Type', choices=contract_type_list, validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    start_date = StringField('Start Date', validators=[DataRequired()])
    position = SelectField('Position', choices=position_list, validators=[DataRequired()])
    department = SelectField('Department', choices=department_list, validators=[DataRequired()])

    base = StringField('Base Salary', validators=[DataRequired(), Regexp('(\d+\.\d+|\d+)', message='Invalid Value')])
    transportation = StringField('Transportation', validators=[DataRequired(), Regexp('(\d+\.\d+|\d+)')])
    house_hold = StringField('House Hold', validators=[DataRequired(), Regexp('(\d+\.\d+|\d+)')])
    currency = RadioField('Currency', choices=[[1, 'Afghani'], [0, 'Dollar']], validators=[DataRequired(), AnyOf(values=["1", "0"])])

    emp_id = HiddenField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Add Contract')

    # TODO validation
    def validate_start_date(self, start_date):
        if start_date.data:
            if not bool(re.match(r'1\d{3}[-\\](0[1-9]|1[0-2])[-\\](0[1-9]|1[0-9]|2[0-9]|3[0-1])', start_date.data)):
                raise ValidationError('Date format is incorrect yyyy-mm-dd')

class leaveRequestForm(FlaskForm):
    leave_type = RadioField('Leave Type', default=1, choices=[[1, 'Hourly'], [0, 'Daily']], validators=[DataRequired(), AnyOf(values=["1", "0"])])
    start_datetime = DateTimeField('From')
    end_datetime = DateTimeField('To')
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(leaveRequestForm, self).__init__()
        self.language = language
        self.leave_type.choices[0][1] = translation_obj.hourly[language]
        self.leave_type.choices[1][1] = translation_obj.daily[language]
        self.leave_type.label.text = translation_obj.leave_type[language]
        self.submit.label.text = translation_obj.send_request[language]
        self.start_datetime.label.text = translation_obj.start_date[language]
        self.end_datetime.label.text = translation_obj.end_date[language]
    def validate_start_datetime (self, start_datetime):
        if not datetime_validation(self, start_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
    def validate_end_datetime (self, end_datetime):
        if not datetime_validation(self, end_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
        # if end_datetime.data is None:
        #     raise ValidationError(message_obj.required_field[self.language].replace('{}', translation_obj.end_date[self.language] + ' '))

class LeaveSupervisorForm(FlaskForm):
    supervisor = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    reason = TextAreaField('Reason for disagreement')
    submit = SubmitField('Send')
    def __init__(self, language):
        super(LeaveSupervisorForm, self).__init__()
        self.language = language
        self.supervisor.choices[0][1] = translation_obj.accept[language]
        self.supervisor.choices[1][1] = translation_obj.reject[language]
        self.supervisor.label.text = translation_obj.confirm_leave_message[language]
        self.reason.label.text = translation_obj.reason_for_disagreement[language]
        self.submit.label.text = translation_obj.send[language]
    def validate_reason (self, reason):
        if reason.data == '':
            raise ValidationError(message_obj.required_field[self.language].replace('{}', translation_obj.reason_for_disagreement[self.language] + ' '))
        elif not re.match("^[A-Za-z0-9- آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ]*$", reason.data):
            raise ValidationError(message_obj.invalid_character[self.language])
        elif len(reason.data) < 20:
            raise ValidationError(message_obj.less_character[self.language].replace('{}', '20'))


class LeaveHRForm(FlaskForm):
    hr = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send')



class ResignRequestForm(FlaskForm):
    reason = StringField(u'Reason', widget=TextArea(), validators=[DataRequired()])
    responsibilities = StringField(u'Responsibilities', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Send Request')


class AddEquipmentForm(FlaskForm):
    equipment = BooleanField('equipment', default=[])
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Add Equipment')

class OvertimeRequestForm(FlaskForm):
    overtime_type = RadioField('Overtime Type', default=1, choices=[[1, 'Hourly'], [0, 'Daily']], validators=[DataRequired(), AnyOf(values=["1", "0"])])
    start_datetime = DateTimeField('From')
    end_datetime = DateTimeField('To')
    description = TextAreaField('Overtime Description')
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(OvertimeRequestForm, self).__init__()
        self.language = language
        self.overtime_type.choices[0][1] = translation_obj.hourly[language]
        self.overtime_type.choices[1][1] = translation_obj.daily[language]
        self.overtime_type.label.text = translation_obj.overtime_type[language]
        self.description.label.text = translation_obj.overtime_description[language]
        self.submit.label.text = translation_obj.send_request[language]
        self.start_datetime.label.text = translation_obj.start_date[language]
        self.end_datetime.label.text = translation_obj.end_date[language]
    def validate_start_datetime (self, start_datetime):
        if not datetime_validation(self, start_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
    def validate_end_datetime (self, end_datetime):
        if not datetime_validation(self, end_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])

class OvertimeSupervisorForm(FlaskForm):
    supervisor = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    reason = TextAreaField('Reason for disagreement')
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(OvertimeSupervisorForm, self).__init__()
        self.language = language
        self.supervisor.choices[0][1] = translation_obj.accept[language]
        self.supervisor.choices[1][1] = translation_obj.reject[language]
        self.supervisor.label.text = translation_obj.confirm_overtime_message[language]
        self.reason.label.text = translation_obj.reason_for_disagreement[language]
        self.submit.label.text = translation_obj.send[language]
    def validate_reason (self, reason):
        if reason.data == '':
            raise ValidationError(message_obj.required_field[self.language].replace('{}', translation_obj.reason_for_disagreement[self.language] + ' '))
        elif not re.match("^[A-Za-z0-9- آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ]*$", reason.data):
            raise ValidationError(message_obj.invalid_character[self.language])
        elif len(reason.data) < 20:
            raise ValidationError(message_obj.less_character[self.language].replace('{}', '20'))

class OvertimeHRForm(FlaskForm):
    hr = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')

class LoanRequestForm(FlaskForm):
    emp_list = [(emp.id, emp.name_english + ' ' + emp.lname_english + '/' + emp.id + '/' + emp.name + ' ' + emp.lname) for emp in Employees.query.all()]
    emp_list.insert(0, ('', '------'))
    requested_amount = StringField('Requested Amount', validators=[Regexp('^[1-9]\d*$'), DataRequired()])
    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    guarantor = SelectField('Guarantor', choices=emp_list, validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanRequestForm, self).__init__()
        self.language = language
    def validate_start_date (self, start_date):
        if not date_validation(self, start_date.data):
            raise ValidationError(message_obj.incorrect_date_format[self.language])
    def validate_end_date (self, end_date):
        if not datetime_validation(self, end_date.data):
            raise ValidationError(message_obj.incorrect_date_format[self.language])

class LoanGuarantorForm(FlaskForm):
    guarantor = RadioField('Guarantor',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')

class LoanHRForm(FlaskForm):
    hr = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')

class LoanPresidencyForm(FlaskForm):
    presidency = RadioField('Presidency',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')

class LoanFinanceForm(FlaskForm):
    finance = RadioField('Finance',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')

class departmentForm(FlaskForm):
    name_department = StringField(' نام دیپارتمنت', validators=[DataRequired()])
    name_english_department = StringField('Name of Department', validators=[DataRequired()])
    submit = SubmitField('Send Request')

class AcceptEquipmentForm(FlaskForm):
    equipment = BooleanField('equipment', default=[])
    submit = SubmitField('Accept')
