from rpc_package import db


# from rpc_package import login_manager
# from flask_login import UserMixin


class Employees(db.Model):
    __table_args__ = {'extend_existing': True}
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
    m_status = db.Column(db.Boolean, nullable=False)
    tin = db.Column(db.Integer, unique=True, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Employee ID: {self.id}, Name: {self.name}, " \
               f"Last name: {self.lname}, Tazkira: {self.tazkira}, TIN: {self.tin}"


class Users(db.Model):
    __table_args__ = {'extend_existing': True}
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'),
                       db.ForeignKey('employees.id'), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)
    role = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    token = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"User ID: {self.emp_id}, role: {self.role}, status: {self.status}"


class User_roles(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_english = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Role ID: {self.id}, role: {self.name}, English role: {self.name_english}"


class Emails(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), db.ForeignKey('employees.id'), unique=True,
                       nullable=False)
    email = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Employee: {self.emp_id}, Email: {self.email}"


class Phone(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), primary_key=True,
                       nullable=False)
    phone = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Employee: {self.emp_id}, Phone: {self.email}"


class Current_addresses(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), primary_key=True,
                       nullable=False)
    address = db.Column(db.String(255), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), primary_key=True, nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Employee: {self.emp_id}, Address: {self.address}, District: {self.district_id}, Province: {self.province_id}"


class Permanent_addresses(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), primary_key=True,
                       nullable=False)
    address = db.Column(db.String(255), nullable=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), primary_key=True, nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"Employee: {self.emp_id}, Address: {self.address}, District: {self.district_id}, Province: {self.province_id}"


class Districts(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    district_name = db.Column(db.String(255), nullable=True)
    province = db.Column(db.Integer, db.ForeignKey('provinces.id'), primary_key=True, nullable=False)
    district_name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"District ID: {self.id}, Name: {self.district_name}, English Name: {self.district_name_english}, Province: {self.province}"


class Provinces(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(255), nullable=True)
    province_name_english = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Province ID: {self.id}, Name: {self.province_name}, English Name: {self.province_name_english}"


class Documents(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.id'), primary_key=True,
                       nullable=False)
    name = db.Column(db.String(255), nullable=True)
    province_name_english = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Document ID: {self.id}, Employee: {self.emp_id}, Name: {self.name}, Path: {self.url}"

# HR Database classes

class Contracts(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20, collation='utf8_general_ci'), db.ForeignKey('employees.employees.id'), primary_key=True, nullable=False)
    pos_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    sal_id = db.Column(db.Integer, db.ForeignKey('salary.id'),  nullable=False)
    contract_type = db.Column(db.Integer, db.ForeignKey('contract_types.id'),  nullable=False)
    contract_duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Contract ID: {self.id}, Employee: {self.emp_id}"

class Contract_types(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    name_english = db.Column(db.String(255), nullable=True)
   
    def __repr__(self):
        return f"Contract Type ID: {self.id}, Name Dari: {self.name}, Name English: {self.name_english}"

class Attendance(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True, nullable=False)
    date = db.Column(db.String(255), nullable=True)
    entrance = db.Column(db.String(255), nullable=True)
    exitTime = db.Column(db.String(255), nullable=True)
    advance = db.Column(db.String(255), nullable=True)
    

    def __repr__(self):
        return f"Attendance ID: {self.id}, Contract ID: {self.cont_id}"

class Departments(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    name_english = db.Column(db.String(255), nullable=True)
   
    def __repr__(self):
        return f"Department ID: {self.id}, Name Dari: {self.name}, Name English: {self.name_english}"

class Positions(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    name_english = db.Column(db.String(255), nullable=True)
   
    def __repr__(self):
        return f"Position ID: {self.id}, Name Dari: {self.name}, Name English: {self.name_english}"

class Position_history(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True, nullable=False)
    pos_id = db.Column(db.Integer, db.ForeignKey('positions.id'), primary_key=True, nullable=False)
    dep_id = db.Column(db.Integer, db.ForeignKey('departments.id'), primary_key=True, nullable=False)
    
    def __repr__(self):
        return f"Position History ID: {self.id}"

class Salary(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    cont_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True, nullable=False)
    base = db.Column(db.String, nullable=False)
    transportation = db.Column(db.String, nullable=False)
    house_hold = db.Column(db.String, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    
    def __repr__(self):
        return f"Salary ID: {self.id}, Contract ID: {self.cont_id}"