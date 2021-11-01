from rpc_package import db, login_manager
from flask_login import UserMixin
from rpc_package.utils import EmployeeValidator

@login_manager.user_loader
def load_user(user_id):
    if EmployeeValidator.emp_id_validator(user_id):
        current_user = Users.query.get(user_id)
        position_history = current_user.employee.position_history.filter_by(status=1).first()
        if position_history :
            current_user.department = position_history.department
        current_user.user_role = User_roles.query.get(current_user.role)
        return current_user
    else:
        return None


class Employees(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "employees"
    id = db.Column(db.String(20, collation='utf8_general_ci'), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    gname = db.Column(db.String(50), nullable=False)
    name_english = db.Column(db.String(50), nullable=True)
    lname_english = db.Column(db.String(50), nullable=True)
    fname_english = db.Column(db.String(50), nullable=True)
    gname_english = db.Column(db.String(50), nullable=True)
    birthday = db.Column(db.Date, nullable=False)
    tazkira = db.Column(db.Integer, unique=True, nullable=False)
    gender = db.Column(db.Boolean, nullable=False)
    blood = db.Column(db.String(10), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)
    m_status = db.Column(db.Boolean, nullable=False)
    tin = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    # Relationship
    position_history = db.relationship("Position_history", foreign_keys='Position_history.emp_id', lazy='dynamic')
    leaves = db.relationship("Leave_form", foreign_keys='Leave_form.emp_id', lazy='dynamic')
    overtimes = db.relationship("Overtime_form", foreign_keys='Overtime_form.emp_id', lazy='dynamic')
    loans = db.relationship("Loan_form", foreign_keys='Loan_form.emp_id', lazy='dynamic')
    users = db.relationship("Users", foreign_keys='Users.emp_id')
    emails = db.relationship("Emails", foreign_keys='Emails.emp_id')
    phones = db.relationship("Phone", foreign_keys='Phone.emp_id', cascade="all, delete")
    documents = db.relationship("Documents", foreign_keys='Documents.emp_id', cascade="all, delete")
    current_address = db.relationship("Current_addresses", foreign_keys='Current_addresses.emp_id', uselist=False, cascade="all, delete")
    permanent_address = db.relationship("Permanent_addresses", foreign_keys='Permanent_addresses.emp_id', uselist=False, cascade="all, delete")

    def __repr__(self):
        return f"Employee ID: {self.id}, Name: {self.name}, " \
               f"Last name: {self.lname}, Tazkira: {self.tazkira}, Profile: {self.profile_pic} TIN: {self.tin}"


class Users(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'),
        db.ForeignKey('employees.id'), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)
    role = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    token = db.Column(db.String(255), nullable=True)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="users")
    user_role = db.relationship('User_roles', foreign_keys=[role], overlaps="users")

    def get_id(self):
        return (self.emp_id)

    def __repr__(self):
        return f"User ID: {self.emp_id}, role: {self.role}, status: {self.status}"


class User_roles(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_english = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Role ID: {self.id}, role: {self.name}, English role: {self.name_english}"


class Emails(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), db.ForeignKey('employees.id'), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=True)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="emails")

    def __repr__(self):
        return f"Employee: {self.emp_id}, Email: {self.email}"


class Phone(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'),
        db.ForeignKey('employees.id'), primary_key=True, nullable=False)
    phone = db.Column(db.String(255), nullable=True)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="phones")

    def __repr__(self):
        return f"Employee: {self.emp_id}, Phone: {self.phone}"


class Current_addresses(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'),
        db.ForeignKey('employees.id'), primary_key=True, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    address_dari = db.Column(db.String(255), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), primary_key=True, nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), primary_key=True, nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="current_address")
    district = db.relationship('Districts', foreign_keys=[district_id], overlaps="current_address")
    province = db.relationship('Provinces', foreign_keys=[province_id], overlaps="current_address")

    def __repr__(self):
        return f"Employee: {self.emp_id}, Address: {self.address}, District: {self.district_id}, Province: {self.province_id}"


class Permanent_addresses(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), primary_key=True,
                       nullable=False)
    address = db.Column(db.String(255), nullable=True)
    address_dari = db.Column(db.String(255), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), primary_key=True, nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), primary_key=True, nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="permanent_address")
    district = db.relationship('Districts', foreign_keys=[district_id], overlaps="permanent_address")
    province = db.relationship('Provinces', foreign_keys=[province_id], overlaps="permanent_address")

    def __repr__(self):
        return f"Employee: {self.emp_id}, Address: {self.address}, District: {self.district_id}, Province: {self.province_id}"


class Districts(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(255), nullable=True)
    province = db.Column(db.Integer, db.ForeignKey('provinces.id'), primary_key=True, nullable=False)
    district_name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"District ID: {self.id}, Name: {self.district_name}, English Name: {self.district_name_english}, Province: {self.province}"


class Provinces(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(255), nullable=True)
    province_name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Province ID: {self.id}, Name: {self.province_name}, English Name: {self.province_name_english}"


class Documents(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), primary_key=True,
                       nullable=False)
    name = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="documents")

    def __repr__(self):
        return f"Document ID: {self.id}, Employee: {self.emp_id}, Name: {self.name}, Path: {self.url}"


# HR Database classes

class Contracts(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'),
                       primary_key=True, nullable=False)
    contract_type = db.Column(db.Integer, db.ForeignKey('contract_types.id'), nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_date = db.Column(db.String(255), nullable=False)
    inserted_by = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'))
    updated_by = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'))
    inserted_date = db.Column(db.DateTime, nullable=True)
    updated_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean(1), nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="contracts")

    def __repr__(self):
        return f"Contract ID: {self.id}, Employee: {self.emp_id}"

class Contract_types(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Contract Type ID: {self.id}, Name Dari: {self.name}, Name English: {self.name_english}"


class Attendance(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True, nullable=False)
    date = db.Column(db.String(255), nullable=True)
    entrance = db.Column(db.String(255), nullable=True)
    exitTime = db.Column(db.String(255), nullable=True)
    advance = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Attendance ID: {self.id}, Contract ID: {self.cont_id}"


class Departments(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Department ID: {self.id}, Name Dari: {self.name}, Name English: {self.name_english}"


class Positions(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Position ID: {self.id}, Name Dari: {self.name}, Name English: {self.name_english}"


class Position_history(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'),
                       primary_key=True, nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), primary_key=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), primary_key=True, nullable=False)
    contract_type_id = db.Column(db.Integer, db.ForeignKey('contract_types.id'), nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_date = db.Column(db.String(255), nullable=False)
    inserted_by = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'))
    updated_by = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'))
    inserted_date = db.Column(db.DateTime, nullable=True)
    updated_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean(1), nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="position_history")
    department = db.relationship('Departments', foreign_keys=[department_id], overlaps="position_history")
    position = db.relationship('Positions', foreign_keys=[position_id], overlaps="position_history")
    contract_type = db.relationship('Contract_types', foreign_keys=[contract_type_id], overlaps="position_history")
    salary = db.relationship("Salary", foreign_keys='Salary.position_history_id', uselist=False)
    def __repr__(self):
        return f"Position History ID: {self.id}"


class Salary(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    position_history_id = db.Column(db.Integer, db.ForeignKey('position_history.id'), primary_key=True, nullable=False)
    base = db.Column(db.String, nullable=False)
    transportation = db.Column(db.String, nullable=False)
    house_hold = db.Column(db.String, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    inserted_by = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'))
    updated_by = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'))
    inserted_date = db.Column(db.DateTime, nullable=True)
    updated_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean(1), nullable=False)
    # Relationship
    position_history = db.relationship('Position_history', foreign_keys=[position_history_id], overlaps="salary")

    def __repr__(self):
        return f"Salary ID: {self.id}, Position History ID: {self.position_history_id}"


class Leave_form(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=False)
    leave_type = db.Column(db.Boolean(1), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=True)
    end_datetime = db.Column(db.Date, nullable=True)
    supervisor = db.Column(db.Boolean, nullable=True)
    supervisor_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    hr = db.Column(db.Boolean, nullable=True)
    hr_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    finalized_at = db.Column(db.DateTime, nullable=False)
    requested_at = db.Column(db.DateTime, nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="leaves")
    re_supervisor = db.relationship('Employees', foreign_keys=[supervisor_id])
    re_hr = db.relationship('Employees', foreign_keys=[hr_id])
    reason = db.relationship("Leave_reason", uselist=False)

    def __repr__(self):
        return f"Leave ID: {self.id}, Employee ID: {self.emp_id}"

class Leave_reason(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    leave_id = db.Column(db.Integer, db.ForeignKey('leave_form.id'), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    # Relationship
    leave = db.relationship('Leave_form', foreign_keys=[leave_id], overlaps="reason")
    def __repr__(self):
        return f"Reason ID: {self.id}, Leave ID: {self.leave_id}, Reason: {self.reason}"


class Overtime_form(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=False)
    overtime_type = db.Column(db.Boolean(1), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=True)
    end_datetime = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=True)
    supervisor = db.Column(db.Boolean, nullable=True)
    supervisor_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    hr = db.Column(db.Boolean, nullable=True)
    hr_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    finalized_at = db.Column(db.DateTime, nullable=False)
    requested_at = db.Column(db.DateTime, nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="overtimes")
    re_supervisor = db.relationship('Employees', foreign_keys=[supervisor_id])
    re_hr = db.relationship('Employees', foreign_keys=[hr_id])
    reason = db.relationship("Overtime_reason", uselist=False)

    def __repr__(self):
        return f"Overtime ID: {self.id}, Employee ID: {self.emp_id}, Overtime Type: {self.overtime_type}"

class Overtime_reason(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    overtime_id = db.Column(db.Integer, db.ForeignKey('overtime_form.id'), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    # Relationship
    overtime = db.relationship('Overtime_form', foreign_keys=[overtime_id], overlaps="reason")
    def __repr__(self):
        return f"Reason ID: {self.id}, Overtime ID: {self.overtime_id}, reason: {self.reason}"

class Loan_form(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "loan_form"
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=False)
    requested_amount = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    guarantor_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=False)
    guarantor = db.Column(db.Boolean, nullable=True)
    hr = db.Column(db.Boolean, nullable=True)
    hr_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    presidency = db.Column(db.Boolean, nullable=True)
    presidency_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    finance = db.Column(db.Boolean, nullable=True)
    finance_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=True)
    finalized_at = db.Column(db.DateTime, nullable=False)
    requested_at = db.Column(db.DateTime, nullable=False)
    # Relationship
    employee = db.relationship('Employees', foreign_keys=[emp_id], overlaps="loans")
    re_guarantor = db.relationship('Employees', foreign_keys=[guarantor_id])
    re_hr = db.relationship('Employees', foreign_keys=[hr_id])
    re_presidency = db.relationship('Employees', foreign_keys=[presidency_id])
    re_finance = db.relationship('Employees', foreign_keys=[finance_id])

    def __repr__(self):
        return f"Loan ID: {self.id}, Employee ID: {self.emp_id}, Requested Amount : {self.requested_amount}"

class Holiday(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "holidays"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255))
    title_english = db.Column(db.String(255))
    def __repr__(self):
        return f"Holiday ID: {self.id}, Date: {self.date}"

class AttendanceFile(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "attendance_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    raw_file_url = db.Column(db.String(255))
    file_url = db.Column(db.String(255))
    def __repr__(self):
        return f"AttendanceFile ID: {self.id}, Year: {self.year}, Month: {self.month}"

class Resign_form(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=False)
    supervisor = db.Column(db.Boolean, nullable=True)
    hr = db.Column(db.Boolean, nullable=True)
    requested_at= db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Resign ID: {self.id}, Employee ID: {self.emp_id}, Reason: {self.reason}"

class Equipment(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    name_english = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    serial = db.Column(db.String(32), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text(0), nullable=False)

    def __repr__(self):
        return f"Equipment ID: {self.id}, Equipment Name: {self.name}"

class Employee_equipment(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    received = db.Column(db.Boolean)
    delivered = db.Column(db.Boolean)

    def __repr__(self):
        return f"Employee_equipment ID: {self.id}, Employee ID: {self.emp_id}"
