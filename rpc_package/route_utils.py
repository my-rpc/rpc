import os
import jdatetime
from rpc_package import db
from rpc_package.rpc_tables import Users, User_roles, Documents, Employees, Phone, Emails, Districts, Provinces, \
    Contracts, Position_history, Salary, Overtime_form,  Resign_form, Contract_types, \
    Employee_equipment, Current_addresses, Permanent_addresses, Leave_form, Departments, \
    Positions, Loan_form

from flask import session
import datetime
from wtforms import StringField, HiddenField
from flask_login import current_user
from rpc_package.forms import ContractForm
from rpc_package.utils import toGregorian, toJalali

def upload_docs(emp_id, request, file_type):
    try:
        request_file = request.files[file_type]
        request_file.filename = f"{file_type}-" + emp_id + ".pdf"
        path = os.path.join(f"./rpc_package/static/files/{file_type}", request_file.filename)
        document = Documents(
            emp_id=emp_id,
            name=file_type,
            url=f"/static/files/{file_type}/" + request_file.filename)
        assert isinstance(db, object)
        request_file.save(path)
        if not Documents.query.filter_by(emp_id=emp_id, name=file_type).first():
            db.session.add(document)
            db.session.commit()
        return 'success'
    except IOError as io:
        return 'error'


def get_profile_info(emp_id):
    profile = db.session.query(Users, User_roles, Employees).join(Users,
                                                                  (Users.role == User_roles.id)).join(Employees, (
            Users.emp_id == Employees.id)).filter(Employees.id == emp_id).first()
    current_address = db.session.query(Current_addresses, Provinces, Districts).join(
        Current_addresses, (Provinces.id == Current_addresses.province_id)).join(Districts, (
            Current_addresses.district_id == Districts.id)
                                                                                 ).filter(
        Current_addresses.emp_id == emp_id).first()
    permanent_address = db.session.query(Permanent_addresses, Provinces, Districts).join(
        Permanent_addresses, (Provinces.id == Permanent_addresses.province_id)).join(Districts, (
            Permanent_addresses.district_id == Districts.id)).filter(
        Permanent_addresses.emp_id == emp_id).first()
    doc_cv = Documents.query.filter_by(emp_id=emp_id, name="cv").first()
    doc_tazkira = Documents.query.filter_by(emp_id=emp_id, name="tazkira").first()
    doc_guarantor = Documents.query.filter_by(emp_id=emp_id, name="guarantor").first()
    doc_tin = Documents.query.filter_by(emp_id=emp_id, name="tin").first()
    doc_education = Documents.query.filter_by(emp_id=emp_id, name="education").first()
    doc_extra = Documents.query.filter_by(emp_id=emp_id, name="extra").first()
    email = Emails.query.filter_by(emp_id=emp_id).first()
    phone = Phone.query.filter_by(emp_id=emp_id).first()
    return profile, current_address, permanent_address, doc_cv, email, phone, doc_tazkira, doc_guarantor, doc_tin, doc_education, doc_extra


def get_documents(emp_id):
    cv_doc = Documents.query.filter_by(emp_id=emp_id, name="cv").first()
    guarantor_doc = Documents.query.filter_by(emp_id=emp_id, name="guarantor").first()
    tazkira_doc = Documents.query.filter_by(emp_id=emp_id, name="tazkira").first()
    education_doc = Documents.query.filter_by(emp_id=emp_id, name="education").first()
    tin_doc = Documents.query.filter_by(emp_id=emp_id, name="tin").first()
    extra_doc = Documents.query.filter_by(emp_id=emp_id, name="extra").first()
    return cv_doc, guarantor_doc, tin_doc, education_doc, extra_doc, tazkira_doc


def upload_profile_pic(request):
    request_file = request.files['profilePic']
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    ext = request_file.filename.split('.')[1]
    if ext in ALLOWED_EXTENSIONS:
        request_file.filename = f"profile-" + session['emp_id'] + "." + ext
        workingdir = os.path.abspath(os.getcwd())
        path = os.path.join(workingdir + "/rpc_package/static/images/profiles", request_file.filename)
        print(workingdir)
        emp = Employees.query.filter_by(id=session['emp_id']).first()
        emp.profile_pic = f"/static/images/profiles/" + request_file.filename
        assert isinstance(db, object)
        request_file.save(path)
        db.session.commit()
        return 'success'
    else:
        return "invalid extention"


def update_employee_data(update_employee_form):
    sel_emp = Employees.query.filter_by(id=update_employee_form.employee_id.data).first()
    phones = Phone.query.filter_by(emp_id=update_employee_form.employee_id.data).all()
    emails = Emails.query.filter_by(emp_id=update_employee_form.employee_id.data).all()
    sel_emp.name = update_employee_form.first_name.data
    sel_emp.lname = update_employee_form.last_name.data
    sel_emp.fname = update_employee_form.father_name.data
    sel_emp.gname = update_employee_form.grand_name.data
    sel_emp.name_english = update_employee_form.first_name_english.data
    sel_emp.lname_english = update_employee_form.last_name_english.data
    sel_emp.fname_english = update_employee_form.father_name_english.data
    sel_emp.gname_english = update_employee_form.grand_name_english.data
    sel_emp.tin = update_employee_form.tin.data
    sel_emp.tazkira = update_employee_form.tazkira.data
    sel_emp.birthday = toGregorian(update_employee_form.birthday.data)
    sel_emp.blood = update_employee_form.blood.data
    sel_emp.m_status = bool(int(update_employee_form.m_status.data))
    sel_emp.gender = bool(int(update_employee_form.gender.data))

    # check if employee has 2 or has 1 or none phone number
    # and check if second phone number is provided
    if phones is not None and len(phones) == 2:
        phones[0].phone = update_employee_form.phone.data
        if update_employee_form.phone_second.data:
            phones[1].phone = update_employee_form.phone_second.data

    elif phones is not None and len(phones) == 1:
        phones[0].phone = update_employee_form.phone.data
        if update_employee_form.phone_second.data:
            phone_second = Phone(
                emp_id=update_employee_form.employee_id.data,
                phone=update_employee_form.phone_second.data
            )
            db.session.add(phone_second)
    elif not phones:
        phone = Phone(
            emp_id=update_employee_form.employee_id.data,
            phone=update_employee_form.phone.data
        )
        db.session.add(phone)

        if update_employee_form.phone_second.data:
            phone_second = Phone(
                emp_id=update_employee_form.employee_id.data,
                phone=update_employee_form.phone_second.data
            )
            db.session.add(phone_second)

    # check if employee has 2 or has 1 or none email address
    # and check if second email address is provided
    if emails is not None and len(emails) == 2:
        emails[0].email = update_employee_form.email.data
        if update_employee_form.email_second.data:
            emails[1].email = update_employee_form.email_second.data

    elif emails is not None and len(emails) == 1:
        update_employee_form.email.data = emails[0].email
        if update_employee_form.email_second.data:
            email_second = Emails(
                emp_id=update_employee_form.employee_id.data,
                email=update_employee_form.email_second.data)
            db.session.add(email_second)
    elif not emails:
        email = Emails(
            emp_id=update_employee_form.employee_id.data,
            email=update_employee_form.email.data)
        db.session.add(email)
        if update_employee_form.email_second.data:
            email_second = Emails(
                emp_id=update_employee_form.employee_id.data,
                email=update_employee_form.email_second.data)
            db.session.add(email_second)

    ###
    #   check if the address data is updated or provided by client
    #   if yes then update data

    if update_employee_form.current_address.data or update_employee_form.current_address_dari.data:
        cur_add = Current_addresses.query.filter_by(emp_id=update_employee_form.employee_id.data).first()

        if cur_add is not None:
            cur_add.province_id = update_employee_form.provinces_current.data
            cur_add.district_id = update_employee_form.district_current.data
            cur_add.address = update_employee_form.current_address.data
            cur_add.address_dari = update_employee_form.current_address_dari.data
        else:

            current_address = Current_addresses(
                emp_id=update_employee_form.employee_id.data,
                address=update_employee_form.current_address.data,
                address_dari=update_employee_form.current_address_dari.data,
                district_id=update_employee_form.district_current.data,
                province_id=update_employee_form.provinces_current.data)
            db.session.add(current_address)

    if update_employee_form.permanent_address.data or update_employee_form.permanent_address_dari.data:
        per_add = Permanent_addresses.query.filter_by(emp_id=update_employee_form.employee_id.data).first()
        if per_add is not None:
            per_add.province_id = update_employee_form.provinces_permanent.data
            per_add.district_id = update_employee_form.district_permanent.data
            per_add.address = update_employee_form.permanent_address.data
            per_add.address_dari = update_employee_form.permanent_address_dari.data
        else:
            permanent_address = Permanent_addresses(
                emp_id=update_employee_form.employee_id.data,
                address=update_employee_form.permanent_address.data,
                address_dari=update_employee_form.permanent_address_dari.data,
                district_id=update_employee_form.district_permanent.data,
                province_id=update_employee_form.provinces_permanent.data)
            db.session.add(permanent_address)
    db.session.commit()


def set_emp_update_form_data(emp_id, update_employee_form):
    emp = Employees.query.get(emp_id)
    phones = Phone.query.filter_by(emp_id=emp_id).all()
    emails = Emails.query.filter_by(emp_id=emp_id).all()
    cur_add = Current_addresses.query.filter_by(emp_id=emp_id).first()
    per_add = Permanent_addresses.query.filter_by(emp_id=emp_id).first()
    update_employee_form.employee_id.data = emp.id
    update_employee_form.first_name.data = emp.name
    update_employee_form.last_name.data = emp.lname
    update_employee_form.father_name.data = emp.fname
    update_employee_form.grand_name.data = emp.gname
    update_employee_form.first_name_english.data = emp.name_english
    update_employee_form.last_name_english.data = emp.lname_english
    update_employee_form.father_name_english.data = emp.fname_english
    update_employee_form.grand_name_english.data = emp.gname_english
    update_employee_form.tin.data = emp.tin
    update_employee_form.tazkira.data = emp.tazkira
    update_employee_form.birthday.data = toJalali(emp.birthday)
    update_employee_form.blood.data = emp.blood

    update_employee_form.gender.data = emp.gender
    update_employee_form.m_status.data = emp.m_status

    cur_address = ''
    cur_district_name = ''
    cur_province_name = ''
    cur_address_eng = ''
    cur_district_name_eng = ''
    cur_province_name_eng = ''

    per_address = ''
    per_district_name = ''
    per_province_name = ''
    per_address_eng = ''
    per_district_name_eng = ''
    per_province_name_eng = ''

    # check if permanent address exists.
    if per_add is not None:
        update_employee_form.provinces_permanent.data = per_add.province_id
        update_employee_form.district_permanent.data = per_add.district_id
        update_employee_form.permanent_address.data = per_add.address
        update_employee_form.permanent_address_dari.data = per_add.address_dari

        per_district = Districts.query.filter_by(id=per_add.district_id).first()
        per_province = Provinces.query.filter_by(id=per_add.province_id).first()

        per_address = per_add.address_dari
        per_district_name = per_district.district_name
        per_province_name = per_province.province_name
        per_address_eng = per_add.address
        per_district_name_eng = per_district.district_name_english
        per_province_name_eng = per_province.province_name_english

    # check if current address exists.
    if cur_add is not None:
        update_employee_form.provinces_current.data = cur_add.province_id
        update_employee_form.district_current.data = cur_add.district_id
        update_employee_form.current_address.data = cur_add.address
        update_employee_form.current_address_dari.data = cur_add.address_dari

        cur_district = Districts.query.filter_by(id=cur_add.district_id).first()
        cur_province = Provinces.query.filter_by(id=cur_add.province_id).first()

        cur_address = cur_add.address_dari
        cur_district_name = cur_district.district_name
        cur_province_name = cur_province.province_name
        cur_address_eng = cur_add.address
        cur_district_name_eng = cur_district.district_name_english
        cur_province_name_eng = cur_province.province_name_english

    # check if employee has 1 or 2 phone and email numbers and set it form field
    if phones is not None and len(phones) == 2:
        update_employee_form.phone.data = phones[0].phone
        update_employee_form.phone_second.data = phones[1].phone
    elif phones is not None and len(phones) == 1:
        update_employee_form.phone.data = phones[0].phone
        update_employee_form.phone_second.data = None
    else:
        update_employee_form.phone.data = None
        update_employee_form.phone_second.data = None

    if emails is not None and len(emails) == 2:
        update_employee_form.email.data = emails[0].email
        update_employee_form.email_second.data = emails[1].email
    elif emails is not None and len(emails) == 1:
        update_employee_form.email.data = emails[0].email
        update_employee_form.email_second.data = None
    else:
        update_employee_form.email.data = None
        update_employee_form.email_second.data = None

    current_addresses = "<div class='py-4 d-flex'><h5 class='text-primary'>ادرس فعلی: </h5>" \
                        + "<p class='px-3'>" \
                        + str(cur_address) + ", " + str(cur_district_name) + ", " + str(
        cur_province_name) + "</p> <br> " \
                        + "<h5 class=' text-primary'> Current address: </h5> <p class='px-3'>" + str(
        cur_address_eng) + ", " \
                        + str(cur_district_name_eng) + ", " + str(cur_province_name_eng) \
                        + "</p> <span onClick=\"showAddress(\'cur-address\')\"> <i class='fad fa-edit text-info'></i> </span> </div>"

    permanent_addresses = "<div class='py-4 d-flex'> <h5 class=' text-primary'> ادرس اصلی: </h5>" \
                          + "<p class='px-3 '>" \
                          + str(per_address) + ", " + str(per_district_name) + ", " + str(
        per_province_name) + "</p> <br>" \
                          + "<h5 class=' text-primary'> Permanent address: </h5> <p class='px-3 '>" \
                          + str(per_address_eng) + ", " + str(per_district_name_eng) + ", " + str(per_province_name_eng) \
                          + "</p> <span onClick=\"showAddress(\'per-address\')\"> <i class='fad fa-edit text-info'></i> </span> </div>"
    return current_addresses, permanent_addresses


def add_leave_request(leave_form, emp_id):
    try:
        if leave_form.leave_type.data == '1':
            leave = Leave_form(
                emp_id=emp_id,
                leave_type=True,
                start_datetime=toGregorian(leave_form.start_datetime.data, '%Y-%m-%d %H:%M:%S'),
                end_datetime=toGregorian(leave_form.end_datetime.data, '%Y-%m-%d %H:%M:%S'),
                requested_at=datetime.datetime.now())
            db.session.add(leave)
        elif leave_form.leave_type.data == '0':
            leave = Leave_form(
                emp_id=emp_id,
                leave_type=False,
                start_datetime=toGregorian(leave_form.start_datetime.data, '%Y-%m-%d %H:%M:%S'),
                end_datetime=toGregorian(leave_form.end_datetime.data, '%Y-%m-%d %H:%M:%S'),
                requested_at=datetime.datetime.now())
            db.session.add(leave)
        db.session.commit()
        return "success"
    except IOError as io:
        return 'error'


def add_overtime_request(overtime_form, emp_id):
    try:
        if overtime_form.overtime_type.data == '1':
            overtime_type = True
        elif overtime_form.overtime_type.data == '0':
            overtime_type = False

        overtime = Overtime_form(
            emp_id=emp_id,
            overtime_type=overtime_type,
            start_datetime=toGregorian(overtime_form.start_datetime.data, '%Y-%m-%d %H:%M:%S'),
            end_datetime=toGregorian(overtime_form.end_datetime.data, '%Y-%m-%d %H:%M:%S'),
            description=overtime_form.description.data,
            requested_at=datetime.datetime.now())
        db.session.add(overtime)
        db.session.commit()
        return "success"
    except IOError as io:
        return 'error'

def add_loan_request(loan_form, emp_id):
    try:
        loan = Loan_form(
            emp_id=emp_id,
            requested_amount=loan_form.requested_amount.data,
            start_date=toGregorian(loan_form.start_date.data),
            end_date=toGregorian(loan_form.end_date.data),
            guarantor_id=loan_form.guarantor.data,
            requested_at=datetime.datetime.now())
        db.session.add(loan)
        db.session.commit()
        return "success"
    except IOError as io:
        return 'error'


def add_contract_form(contract_form):
    try:
        add_contract = Contracts(
            emp_id=contract_form.emp_id.data,
            end_date=toGregorian(contract_form.end_date.data),
            contract_type=contract_form.contract_type.data,
            start_date=toGregorian(contract_form.start_date.data),
            inserted_by=current_user.emp_id,
            inserted_date=datetime.datetime.now().strftime("%Y-%m-%d"),
            status = 1
        )
        db.session.add(add_contract)
        db_commit = db.session.commit()
        db.session.flush(add_contract)

        if add_contract.id is not None:
            add_contract_position = Position_history(
                position_id=contract_form.position.data,
                contract_id=add_contract.id,
                department_id=contract_form.department.data,
                inserted_by=current_user.emp_id,
                inserted_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                status=1
            )

            add_contract_salary = Salary(
                contract_id=add_contract.id,
                base=contract_form.base.data,
                transportation=contract_form.transportation.data,
                house_hold=contract_form.house_hold.data,
                currency=contract_form.currency.data,
                inserted_by=current_user.emp_id,
                inserted_date=datetime.datetime.now().strftime("%Y-%m-%d"),
                status=1
            )
        db.session.add(add_contract_position)
        db.session.add(add_contract_salary)
        db.session.commit()
        return "success"
    except IOError as io:
        return 'error'


def send_resign_request(resign_form, emp_id):
    resign = Resign_form(
        emp_id=emp_id,
        reason=resign_form.reason.data,
        responsibilities=resign_form.responsibilities.data)
    db.session.add(resign)
    if db.session.commit():
        return "success"
    else:
        return "error"

def assign_equipment(request, emp_id):
    equipment = ""
    for eq in request.form.getlist('equipment'):
        have_equipment = Employee_equipment.query.filter_by(emp_id=emp_id, equipment_id=eq).first()
        if have_equipment is None:
            equipment = Employee_equipment(
            emp_id=emp_id,
            equipment_id=eq)
            db.session.add(equipment)
    if db.session.commit():
        return "success"
    else:
        return "error"


def send_department(department_form):
    department = Departments(
        name=department_form.name_department.data,
        name_english=department_form.name_english_department.data)
    db.session.add(department)
    if db.session.commit():
        return "success"
    else:
        return "error"


def set_contact_update_form_data(contract_id, contract_form):
    try:

        contract = Contracts.query.filter_by(id = contract_id).first()
        position = Position_history.query.filter_by(contract_id = contract_id, status = True).first()
        salary = Salary.query.filter_by(contract_id = contract_id, status = True).first()

        contract_form.emp_id.data = contract.emp_id
        contract_form.end_date.data = toJalali(contract.end_date)
        contract_form.contract_type.data = contract.contract_type
        contract_form.start_date.data = contract.start_date

        setattr(contract_form, 'contract_id', HiddenField('Contract ID'))
        contract_id = contract_form.contract_id.bind(contract_form, 'contract_id')
        contract_form._fields['contract_id'] = contract_id
        contract_form._fields['contract_id'].data = contract.id

        if position:
            contract_form.position.data = position.position_id
            contract_form.department.data = position.department_id
            # addmin new field for position history ID
            setattr(contract_form, 'position_id', HiddenField('Position ID'))
            position_id = contract_form.position_id.bind(contract_form, 'position_id')
            contract_form._fields['position_id'] = position_id
            contract_form._fields['position_id'].data = position.id
        else:
            contract_form.position.data = ''
            contract_form.department.data = ''
            # addmin new field for position history ID
            setattr(contract_form, 'position_id', HiddenField('Position ID'))
            position_id = contract_form.position_id.bind(contract_form, 'position_id')
            contract_form._fields['position_id'] = position_id
            contract_form._fields['position_id'].data = ''

        if salary:
            contract_form.base.data = salary.base
            contract_form.transportation.data = salary.transportation
            contract_form.house_hold.data = salary.house_hold
            contract_form.currency.data = salary.currency

            setattr(contract_form, 'salary_id', HiddenField('Salary ID'))
            salary_id = contract_form.salary_id.bind(contract_form, 'salary_id')
            contract_form._fields['salary_id'] = salary_id
            contract_form._fields['salary_id'].data = salary.id
        else:
            contract_form.base.data = ''
            contract_form.transportation.data = ''
            contract_form.house_hold.data = ''
            contract_form.currency.data = ''
            setattr(contract_form, 'salary_id', HiddenField('Salary ID'))
            salary_id = contract_form.salary_id.bind(contract_form, 'salary_id')
            contract_form._fields['salary_id'] = salary_id
            contract_form._fields['salary_id'].data = ''


    except IOError as io:
        return 'error'
    return contract_form.contract_type.data, contract_form.position.data, contract_form.department.data


def update_contract(req, contract_form):
    try:
        contract = Contracts.query.filter_by(id = req.form['contract_id']).first()
        position = Position_history.query.filter_by(id = req.form['position_id']).first()
        salary = Salary.query.filter_by(id = req.form['salary_id']).first()
        pos = Positions.query.filter_by(id = position.position_id).first()
        dep = Departments.query.filter_by(id = position.department_id).first()
        contract_type = Contract_types.query.filter_by(id = contract.contract_type).first()

        contract.contract_type = contract_form.contract_type.data
        contract.end_date = toGregorian(contract_form.end_date.data)
        contract.start_date= toGregorian(contract_form.start_date.data)
        contract.updated_by= current_user.emp_id
        contract.updated_date = datetime.datetime.now()

        salary.base = contract_form.base.data
        salary.transportation = contract_form.transportation.data
        salary.house_hold = contract_form.house_hold.data
        salary.currency = contract_form.currency.data
        salary.updated_by= current_user.emp_id
        salary.updated_date = datetime.datetime.now()

        position.position_id = contract_form.position.data
        position.department_id = contract_form.department.data
        position.updated_by= current_user.emp_id
        position.updated_date = datetime.datetime.now()
        if session['language'] == 'en':
            position_name = pos.name_english
            department_name = dep.name_english
            contract_type_name = contract_type.name_english
            if contract_form.currency.data == '1':
                currency = 'AFG'
            else:
                currency = 'Dollar'
        else:
            department_name = dep.name
            position_name = pos.name
            contract_type_name = contract_type.name
            if contract_form.currency.data == '1':
                currency = 'افغانی'
            else:
                currency = 'دالر'
        delta_time  = datetime.datetime.strptime(contract.end_date, '%Y-%m-%d') - datetime.datetime.strptime(contract.start_date, '%Y-%m-%d')
        year = delta_time.days / 30 / 12
        month = delta_time.days / 30 % 12
        duration = str(int(year)) + 'years and ' if year > 1 else 'year and' \
            + str(int(month)) + 'months' if month > 1 else 'month'
        data = {
            "contract": {
                "contract_id": req.form['contract_id'],
                "contract_type": contract_type_name,
                "start_date": contract_form.start_date.data,
                "end_date": contract_form.end_date.data,
                "duration": duration,
                "updated_by": current_user.emp_id,
            },"salary": {
                "base": contract_form.base.data,
                "transportation": contract_form.transportation.data,
                "house_hold": contract_form.house_hold.data,
                "currency": currency,
            },
            "position": {
                "position": position_name,
                "position_id": contract_form.position.data,
                "department": department_name,
                "department_id": contract_form.department.data,
                "updated_by": current_user.emp_id,
            },
        }
        db.session.commit()
    except IOError as io:
        return 'error'
    return data


def accept_equipment(request, owner):
    equipment=""
    for eq in request.form.getlist('equipment'):
        my_equipment = Employee_equipment.query.filter_by(id=eq).first()
        # if my_equipment is None:
        if owner == "employee":
            my_equipment.received = True
        elif owner == "admin":
            my_equipment.delivered = True

    try:
        db.session.add(my_equipment)
        db.session.commit()
        return "success"
    except IOError as io:
        return 'error'


def accept_reject_resign(request):
    resign_id = request.args.get('resign')
    action = request.args.get("action")
    if action == "1":
        action = True
    elif action == "0":
        action = False
    resign = Resign_form.query.filter_by(id=resign_id).first()
    resign.hr = action

    try:
        db.session.add(resign)
        db.session.commit()
        return "success"
    except IOError as io:
        return 'error'