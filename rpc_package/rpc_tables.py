from rpc_package import db
# from rpc_package import login_manager
# from flask_login import UserMixin


class Employees(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.String(20), primary_key=True)
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
    emp_id = db.Column(db.String(20), db.ForeignKey('employees.id'), nullable=False, primary_key=True)
    password = db.Column(db.String(60), nullable=True)
    # TODO db.ForeignKey of role table
    role = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Boolean, nullable=False)
    token = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"User ID: {self.emp_id}, role: {self.role}, status: {self.status}"
