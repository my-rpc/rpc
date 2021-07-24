from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from rpc_package import app, pass_crypt, db
from werkzeug.utils import secure_filename
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm, UploadCVForm
from rpc_package.form_dynamic_language import *
from rpc_package.rpc_tables import Users, Employees, User_roles, Permanent_addresses, Current_addresses, Districts, \
    Emails, Phone, Provinces
from rpc_package.utils import EmployeeValidator, message_to_client_403, message_to_client_200
import os
from datetime import datetime
from sqlalchemy.orm import aliased


@app.route("/", methods=['GET', 'POST'])
@login_required
def blank():
    return render_template('blank.html', language='en', translation=translation_obj)


@app.route("/create_new_user", methods=['GET', 'POST'])
@login_required
def create_new_user():
    language = 'en'
    create_new_user_form = CreateUserForm()
    if request.method == 'POST':
        if create_new_user_form.validate_on_submit():
            hashed_pass = pass_crypt.generate_password_hash(create_new_user_form.password.data).decode('utf=8')
            new_user = Users(
                emp_id=create_new_user_form.employee_id.data,
                password=hashed_pass,
                role=create_new_user_form.user_role.data,
                status=1,
                token='adding new token')
            try:
                db.session.add(new_user)
                db.session.commit()
            except IOError as exc:
                return message_to_client_403(message_obj.create_new_user_not[language])
            return message_to_client_200(
                message_obj.create_new_user_save[language].format(create_new_user_form.employee_id.data))
        else:
            return message_to_client_403(create_new_user_form.errors)
    users = db.session.query(Users, User_roles, Employees).join(Users,
                                                                (Users.role == User_roles.id)).join(Employees, (
            Users.emp_id == Employees.id)).all()

    create_new_user_form = update_messages_user(create_new_user_form, language)
    return render_template('create_new_user.html', title='Create New User', users=users,
                           form=create_new_user_form, language=language, translation=translation_obj,
                           message_obj=message_obj)


@app.route("/uds_user", methods=['GET', 'POST'])
@login_required
def uds_user():
    language = 'en'
    if request.method == 'POST':
        if EmployeeValidator.emp_id_validator(request.form['employee_id']) and \
                EmployeeValidator.number_validator(request.form['user_role']):
            user = Users.query.get(request.form['employee_id'])
            try:
                user.status = bool(int(request.form['status']))
                user.role = request.form['user_role']
                db.session.commit()
            except IOError as exc:
                return message_to_client_403(message_obj.create_new_user_update_not[language])
            return message_to_client_200(
                message_obj.create_new_user_update[language].format(request.form['employee_id']))
        else:
            return message_to_client_403(message_obj.create_new_user_update_not[language])
    user_id = request.args.get('user_id')
    if EmployeeValidator.emp_id_validator(user_id):
        user = Users.query.get(user_id)
        role_list = [(role.id, role.name_english, role.name) for role in User_roles.query.all()]

        return ({'user': {'emp_id': user.emp_id, 'role': user.role,
                          'status': user.status}, 'user_role': role_list,
                 'language': language,
                 'translation': translation_obj.__dict__,
                 'message_obj': message_obj.__dict__})
    else:
        message_to_client_403(message_obj.invalid_message[language])


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Login part
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blank"))
    default_language = 'en'

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = Users.query.filter_by(emp_id=login_form.username.data).first()
        if user and pass_crypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            request_user_page = request.args.get('next')
            if request_user_page:
                return redirect(request_user_page)
            else:
                return redirect(url_for("blank"))
        else:
            return message_to_client_403(message_obj.password_incorrect[default_language])

    return render_template('login.html', title='Login',
                           form=login_form, language=default_language,
                           translation=translation_obj, message_obj=message_obj)


@app.route("/add_employee", methods=['GET', 'POST'])
@login_required
def add_employee():
    language = 'en'
    add_employee_form = EmployeeForm()
    if request.method == 'POST':
        if add_employee_form.validate_on_submit():
            new_employee = Employees(
                id=add_employee_form.employee_id.data,
                name=add_employee_form.first_name.data,
                lname=add_employee_form.last_name.data,
                fname=add_employee_form.father_name.data,
                gname=add_employee_form.grand_name.data,
                name_english=add_employee_form.first_name_english.data,
                lname_english=add_employee_form.last_name_english.data,
                fname_english=add_employee_form.father_name_english.data,
                gname_english=add_employee_form.grand_name_english.data,
                birthday=add_employee_form.birthday.data,
                tazkira=add_employee_form.tazkira.data,
                gender=True if add_employee_form.gender.data else False,
                blood=add_employee_form.blood.data,
                m_status=True if add_employee_form.m_status.data else False,
                tin=add_employee_form.tin.data,
                status=1)
            db.session.add(new_employee)
            db.session.commit()
            permanent_address = Permanent_addresses(
                emp_id=add_employee_form.employee_id.data,
                address=add_employee_form.permanent_address.data,
                address_dari=add_employee_form.permanent_address_dari.data,
                district_id=add_employee_form.district_permanent.data,
                province_id=add_employee_form.provinces_permanent.data)
            current_address = Current_addresses(
                emp_id=add_employee_form.employee_id.data,
                address=add_employee_form.current_address.data,
                address_dari=add_employee_form.current_address_dari.data,
                district_id=add_employee_form.district_current.data,
                province_id=add_employee_form.provinces_current.data)
            if add_employee_form.email.data:
                email = Emails(
                    emp_id=add_employee_form.employee_id.data,
                    email=add_employee_form.email.data)
                db.session.add(email)
            if add_employee_form.email_second.data:
                email_second = Emails(
                    emp_id=add_employee_form.employee_id.data,
                    email=add_employee_form.email_second.data)
                db.session.add(email_second)
            phone = Phone(
                emp_id=add_employee_form.employee_id.data,
                phone=add_employee_form.phone.data)
            if add_employee_form.phone_second.data:
                phone_second = Phone(
                    emp_id=add_employee_form.employee_id.data,
                    phone=add_employee_form.phone_second.data)
                db.session.add(phone_second)
            try:
                db.session.add(permanent_address)
                db.session.add(current_address)
                db.session.add(phone)
                db.session.commit()
            except IOError as exc:
                return message_to_client_403(message_obj.create_new_employee_not[language])
            return message_to_client_200(
                message_obj.create_new_employee_save[language].format(add_employee_form.employee_id.data))
        else:
            return message_to_client_403(add_employee_form.errors)

    add_employee_form = update_messages_employee(add_employee_form, language)
    return render_template('add_employee.html', title='Add Employee',
                           form=add_employee_form, language=language,
                           translation=translation_obj, message_obj=message_obj)


@app.route("/add_documents", methods=['GET', 'POST'])
@login_required
def add_documents():
    language = 'en'
    cv_form = UploadCVForm()
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        cv = request.files['cv']
        path = os.path.join(workingdir, cv.filename)
        cv.save(path)
        return path
    return render_template("add_documents.html", title='Add Employee Documents',
                           language=language,
                           translation=translation_obj, form=cv_form, message_obj=message_obj)


@app.route("/load_districts", methods=['POST'])
@login_required
def load_districts():
    if request.method == "POST":
        province = request.args.get("province")
        districts = {district.id: district.district_name + "/" + district.district_name_english for district in
                     Districts.query.filter_by(province=province).all()}
        return jsonify(districts)


@app.route("/employee_settings", methods=['GET', 'POST'])
@login_required
def employee_settings():
    language = 'en'

    employees = db.session.query(Employees).all()
    phones = {}
    emails = {}
    for x, emp in enumerate(employees):
        phone = db.session.query(Phone).filter_by(emp_id=emp.id).all()
        email = db.session.query(Emails).filter_by(emp_id=emp.id)
        if phone is not None:
            phones[x] = phone
        if email is not None:
            emails[x] = email
    print(emails)

    return render_template("employee_settings.html", title='Employee Settings',
                           employees=employees, emails=emails, phones=phones, language=language,
                           translation=translation_obj, message_obj=message_obj)


@app.route('/employee_details', methods=['GET', "POST"])
@login_required
def employee_details():
    language = 'en'
    return render_template('employee_details.html', title='Employee Details', language=language,
                           translation=translation_obj, message_obj=message_obj)


@app.route('/uds_employee', methods=['GET', "POST"])
@login_required
def uds_employee():
    language = 'en'

    update_employee_form = EmployeeForm()
    emp_id = request.args.get('emp_id')
    if EmployeeValidator.emp_id_validator(emp_id):

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
        update_employee_form.last_name_english.data = emp.name_english
        update_employee_form.father_name_english.data = emp.name_english
        update_employee_form.grand_name_english.data = emp.name_english
        update_employee_form.tin.data = emp.tin
        update_employee_form.tazkira.data = emp.tazkira
        update_employee_form.birthday.data = emp.birthday
        update_employee_form.blood.data = emp.blood

        update_employee_form.gender.data = emp.gender
        update_employee_form.m_status.data = emp.m_status

        if per_add is not None:
            update_employee_form.provinces_permanent.data = per_add.province_id
            update_employee_form.district_permanent.data = per_add.district_id
            update_employee_form.permanent_address.data = per_add.address
            update_employee_form.permanent_address_dari.data = per_add.address_dari

        if cur_add is not None:
            update_employee_form.provinces_current.data = cur_add.province_id
            update_employee_form.district_current.data = cur_add.district_id
            update_employee_form.current_address.data = cur_add.address
            update_employee_form.current_address_dari.data = cur_add.address_dari

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
        cur_district = Districts.query.filter_by(id=cur_add.district_id).first()
        cur_province = Provinces.query.filter_by(id=cur_add.province_id).first()
        per_district = Districts.query.filter_by(id=per_add.district_id).first()
        per_province = Provinces.query.filter_by(id=per_add.province_id).first()

        current_addresses = "<div class='py-4'><h5 class='d-inline text-primary'> \
                            Current address: </h5><p class='px-3 d-inline'>" + cur_add.address + ", " \
                            + cur_district.district_name + ", " + cur_province.province_name \
                            + "</p> <span onClick=\"showAddress(\'cur-address\')\"> <i class='fad fa-edit text-info'></i> </span> </div>"

        permanent_addresses = "<div class='py-4'> <h5 class='d-inline text-primary'> \
                            Permanent address: </h5><p class='px-3 d-inline'>" + cur_add.address + ", " \
                              + per_district.district_name + ", " + per_province.province_name \
                              + "</p> <span onClick=\"showAddress(\'per-address\')\"> <i class='fad fa-edit text-info'></i> </span> </div>"

        data = jsonify(render_template('ajax_template/update_employee_form.html', language=language, 
                            form=update_employee_form, translation=translation_obj, message_obj=message_obj), 
                            {'current_add': current_addresses, 'permanent_add': permanent_addresses})
        return data
    else:
        message_to_client_403(message_obj.invalid_message[language])
