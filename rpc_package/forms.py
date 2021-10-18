from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, SubmitField, BooleanField, RadioField, \
     DecimalField, DateField, TimeField, IntegerField, SelectField, FileField,  TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError, AnyOf
import re
from wtforms.widgets import TextArea
from rpc_package.rpc_tables import Provinces, Districts, User_roles, Employees, Emails, Phone, Contract_types, \
    Positions, Departments, Salary, Holiday
from rpc_package.utils import check_language, datetime_validation, date_validation, to_gregorian, get_months
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
    def __init__(self, language):
        super(CreateUserForm, self).__init__()
        self.language = language
        self.employee_id.label.text = translation_obj.employee_id[language]
        self.employee_id.validators[2].message = message_obj.wrong_format[language].format("Employee ID")
        self.password.label.text = translation_obj.password[language]
        self.password.validators[1].message = message_obj.check_length[language].format(str(6), "")
        self.confirm_password.label.text = translation_obj.confirm_password[language]
        self.confirm_password.validators[1].message = message_obj.equal[language]
        self.user_role.label.text = translation_obj.user_role[language]
        self.submit.label.text = translation_obj.submit_user[language]
        self.employee_id.validators[1].message = message_obj.check_length[language].format(str(8), "Employee ID")

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

    def __init__(self, language):
        super(EmployeeForm,self).__init__()
        self.language = language
        self.employee_id.label.text = translation_obj.employee_id[language]
        self.tazkira.label.text = translation_obj.tazkira[language]
        self.birthday.label.text = translation_obj.date_of_birth[language]
        self.gender.label.text = translation_obj.gender[language]
        self.gender.choices[0][1] = translation_obj.male[language]
        self.gender.choices[1][1] = translation_obj.female[language]
        self.m_status.label.text = translation_obj.status[language]
        self.m_status.choices[0][1] = translation_obj.married[language]
        self.m_status.choices[1][1] = translation_obj.single[language]
        self.email.label.text = translation_obj.email[language]
        self.email_second.label.text = translation_obj.email_second[language]
        self.phone_second.label.text = translation_obj.phone_second[language]
        self.phone.label.text = translation_obj.phone[language]
        self.permanent_address.label.text = translation_obj.permanent_address[language]
        self.current_address.label.text = translation_obj.current_address[language]
        self.provinces_permanent.label.text = translation_obj.provinces[language]
        self.provinces_current.label.text = translation_obj.provinces[language]
        self.district_permanent.label.text = translation_obj.district[language]
        self.district_current.label.text = translation_obj.district[language]
        self.submit.label.text = translation_obj.add_new_employee[language]

    def validate_email(self, email):
        if email.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.email[self.language]))
        elif not bool(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email.data)):
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
    def __init__(self, language):
        super(ContractForm, self).__init__()
        self.language = language
        self.contract_type.label.text = translation_obj.contract_type[language]
        self.end_date.label.text = translation_obj.end_date[language]
        self.start_date.label.text = translation_obj.start_date[language]
        self.position.label.text = translation_obj.position[language]
        self.department.label.text = translation_obj.department[language]
        self.base.label.text = translation_obj.base_salary[language]
        self.transportation.label.text = translation_obj.transportation[language]
        self.house_hold.label.text = translation_obj.house_hold[language]
        self.currency.label.text = translation_obj.currency[language]

    # TODO validation
    def validate_start_date(self, start_date):
        if start_date.data:
            if not bool(re.match(r'1\d{3}[-\\](0[1-9]|1[0-2])[-\\](0[1-9]|1[0-9]|2[0-9]|3[0-1])', start_date.data)):
                raise ValidationError('Date format is incorrect yyyy-mm-dd')

class leaveRequestForm(FlaskForm):
    leave_type = RadioField('Leave Type', default=1, choices=[[1, 'Hourly'], [0, 'Daily']], validators=[DataRequired(), AnyOf(values=["1", "0"])])
    start_datetime = StringField('Start Date')
    end_datetime = StringField('End Date')
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
        if start_datetime.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.start_date[self.language]))
        elif not datetime_validation(self, start_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
    def validate_end_datetime (self, end_datetime):
        if end_datetime.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.end_date[self.language]))
        elif not datetime_validation(self, end_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
        elif isinstance(end_datetime.data, str) and self.leave_type.data == '1':
            date_format = '%Y-%m-%d %H:%M:%S'
            diff = jdatetime.datetime.strptime(end_datetime.data, date_format) - jdatetime.datetime.strptime(self.start_datetime.data, date_format)
            if diff > datetime.timedelta(hours=8):
                raise ValidationError(message_obj.more_leave_duration[self.language])
            elif diff < datetime.timedelta(hours=1):
                raise ValidationError(message_obj.less_leave_duration[self.language])     

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
        if self.supervisor.data == '0':
            if reason.data == '':
                raise ValidationError(message_obj.required_field[self.language].replace('{}', translation_obj.reason_for_disagreement[self.language] + ' '))
            elif not re.match("^[A-Za-z0-9- .آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ]*$", reason.data):
                raise ValidationError(message_obj.invalid_character[self.language])
            elif len(reason.data) < 20:
                raise ValidationError(message_obj.less_character[self.language].replace('{}', '20'))


class LeaveHRForm(FlaskForm):
    hr = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send')
    def __init__(self, language):
        super(LeaveHRForm, self).__init__()
        self.language = language
        self.hr.choices[0][1] = translation_obj.accept[language]
        self.hr.choices[1][1] = translation_obj.reject[language]
        self.hr.label.text = translation_obj.confirm_leave_message[language]
        self.submit.label.text = translation_obj.send[language]

class ResignRequestForm(FlaskForm):
    reason = StringField(u'Reason', widget=TextArea(), validators=[DataRequired()])
    responsibilities = StringField(u'Responsibilities', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(ResignRequestForm, self).__init__()
        self.language = language
        self.reason.label.text = translation_obj.resign_reason[language]
        self.submit.label.text = translation_obj.send_request[language]
        self.responsibilities.label.text = translation_obj.responsibilities[language]

class AddEquipmentForm(FlaskForm):
    equipment = BooleanField('equipment', default=[])
    emp_id = HiddenField('Employee ID', validators=[DataRequired()])
    submit = SubmitField('Add Equipment')

class OvertimeRequestForm(FlaskForm):
    overtime_type = RadioField('Overtime Type', default=1, choices=[[1, 'Hourly'], [0, 'Daily']], validators=[DataRequired(), AnyOf(values=["1", "0"])])
    start_datetime = StringField('Start Date')
    end_datetime = StringField('End Date')
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
        if start_datetime.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.start_date[self.language]))
        if not datetime_validation(self, start_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
    def validate_end_datetime (self, end_datetime):
        if end_datetime.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.end_date[self.language]))
        elif not datetime_validation(self, end_datetime.data):
            raise ValidationError(message_obj.incorrect_datetime_format[self.language])
        elif isinstance(end_datetime.data, str) and self.overtime_type.data == '1':
            date_format = '%Y-%m-%d %H:%M:%S'
            diff = jdatetime.datetime.strptime(end_datetime.data, date_format) - jdatetime.datetime.strptime(self.start_datetime.data, date_format)
            if diff > datetime.timedelta(hours=8):
                raise ValidationError(message_obj.more_overtime_duration[self.language])
            elif diff < datetime.timedelta(hours=1):
                raise ValidationError(message_obj.less_overtime_duration[self.language])

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
        if self.supervisor.data == '0':
            if reason.data == '':
                raise ValidationError(message_obj.required_field[self.language].replace('{}', translation_obj.reason_for_disagreement[self.language] + ' '))
            elif not re.match("^[A-Za-z0-9- .آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ]*$", reason.data):
                raise ValidationError(message_obj.invalid_character[self.language])
            elif len(reason.data) < 20:
                raise ValidationError(message_obj.less_character[self.language].replace('{}', '20'))

class OvertimeHRForm(FlaskForm):
    hr = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(OvertimeHRForm, self).__init__()
        self.language = language
        self.hr.choices[0][1] = translation_obj.accept[language]
        self.hr.choices[1][1] = translation_obj.reject[language]
        self.hr.label.text = translation_obj.confirm_overtime_message[language]
        self.submit.label.text = translation_obj.send[language]

class LoanRequestForm(FlaskForm):
    requested_amount = StringField('Requested Amount', validators=[Regexp('^[1-9]\d*$'), DataRequired()])
    start_date = StringField('Start Date')
    end_date = StringField('End Date')
    guarantor = StringField('Guarantor')
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanRequestForm, self).__init__()
        self.language = language
        self.requested_amount.label.text = translation_obj.requested_amount[language]
        self.guarantor.label.text = translation_obj.guarantor[language]
        self.submit.label.text = translation_obj.send_request[language]
        self.start_date.label.text = translation_obj.repayment_start_date[language]
        self.end_date.label.text = translation_obj.repayment_end_date[language]
    def validate_start_date (self, start_date):
        if start_date.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.start_date[self.language]))
        elif not date_validation(self, start_date.data):
            raise ValidationError(message_obj.incorrect_date_format[self.language])
    def validate_end_date (self, end_date):
        if end_date.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.end_date[self.language]))
        elif not date_validation(self, end_date.data):
            raise ValidationError(message_obj.incorrect_date_format[self.language])
    def validate_guarantor (self, guarantor):
        if guarantor.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.guarantor[self.language]))

class LoanGuarantorForm(FlaskForm):
    guarantor = RadioField('Guarantor',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanGuarantorForm, self).__init__()
        self.language = language
        self.guarantor.choices[0][1] = translation_obj.accept[language]
        self.guarantor.choices[1][1] = translation_obj.reject[language]
        self.guarantor.label.text = translation_obj.guarantor_confirm_loan_message[language]
        self.submit.label.text = translation_obj.send[language]

class LoanHRForm(FlaskForm):
    hr = RadioField('HR',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanHRForm, self).__init__()
        self.language = language
        self.hr.choices[0][1] = translation_obj.accept[language]
        self.hr.choices[1][1] = translation_obj.reject[language]
        self.hr.label.text = translation_obj.hr_confirm_loan_message[language]
        self.submit.label.text = translation_obj.send[language]

class LoanPresidencyForm(FlaskForm):
    presidency = RadioField('Presidency',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanPresidencyForm, self).__init__()
        self.language = language
        self.presidency.choices[0][1] = translation_obj.accept[language]
        self.presidency.choices[1][1] = translation_obj.reject[language]
        self.presidency.label.text = translation_obj.presidency_confirm_loan_message[language]
        self.submit.label.text = translation_obj.send[language]

class LoanFinanceForm(FlaskForm):
    finance = RadioField('Finance',
        choices=[[1, 'Approved'], [0, 'Rejected']],
        validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanFinanceForm, self).__init__()
        self.language = language
        self.finance.choices[0][1] = translation_obj.accept[language]
        self.finance.choices[1][1] = translation_obj.reject[language]
        self.finance.label.text = translation_obj.finance_confirm_loan_message[language]
        self.submit.label.text = translation_obj.send[language]

class HolidayForm(FlaskForm):
    date = StringField('Date')
    title = StringField('عنوان')
    title_english = StringField('Title')
    submit = SubmitField('Submit')
    def __init__(self, language):
        super(HolidayForm, self).__init__()
        self.language = language
        self.date.label.text = translation_obj.date[language]
        self.submit.label.text = translation_obj.save[language]
    def validate_date (self, date):
        if date.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.date[self.language]))
        elif not date_validation(self, date.data):
            raise ValidationError(message_obj.incorrect_date_format[self.language])
        else:
            holiday = Holiday.query.filter_by(date=to_gregorian(date.data)).first()
            if holiday:
                raise ValidationError(message_obj.duplicate_entry[self.language].format(translation_obj.date[self.language]))
    def validate_title (self, title):
        if title.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.title[self.language]))
        elif not check_language(title.data):
            raise ValidationError("عنوان باید به دری نوشته شود.")
    def validate_title_english (self, title_english):
        if title_english.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.english_title[self.language]))

class AttendanceForm(FlaskForm):
    year = jdatetime.date.today().year
    year = SelectField('Year', choices=[year-1, year, year+1])
    month = SelectField('Month', choices=get_months())
    raw_file_url = FileField('Select Attendance File')
    submit = SubmitField('Submit')
    def __init__(self, language):
        super(AttendanceForm, self).__init__()
        self.language = language
        self.year.label.text = translation_obj.year[language]
        self.month.label.text = translation_obj.month[language]
        self.submit.label.text = translation_obj.save[language]
    def validate_year (self, year):
        if year.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.year[self.language]))
    def validate_month (self, month):
        if month.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.month[self.language]))
    def validate_raw_file_url (self, raw_file_url):
        if raw_file_url.data == '':
            raise ValidationError(message_obj.required_field[self.language].format(translation_obj.attendance_file[self.language]))
        # elif not re.match(r"^.*\.(xlsx|xlsm|xlsb|xls)$", raw_file_url.data):
        #     raise ValidationError(message_obj.file_format_excel[self.language])

class departmentForm(FlaskForm):
    name_department = StringField(' نام دیپارتمنت', validators=[DataRequired()])
    name_english_department = StringField('Name of Department', validators=[DataRequired()])
    submit = SubmitField('Send Request')
    def __init__(self, language):
        super(LoanRequestForm, self).__init__()
        self.language = language
        self.name_department.label.text = translation_obj.name_department[language]
        self.name_english_department.label.text = translation_obj.name_english_department[language]
        self.submit.label.text = translation_obj.send_request[language]

class AcceptEquipmentForm(FlaskForm):
    equipment = BooleanField('equipment', default=[])
    submit = SubmitField('Accept')
