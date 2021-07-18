from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from rpc_package import app, pass_crypt, db
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm
from rpc_package.form_dynamic_language import *
from rpc_package.rpc_tables import Users, Employees, User_roles, Permanent_addresses, Current_addresses, Districts, \
    Emails, Phone
from rpc_package.utils import EmployeeValidator, message_to_client_403, message_to_client_200
import json


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
def add_documents():
    language = 'en'
    return render_template("add_documents.html", title='Add Employee Documents',
                           language=language,
                           translation=translation_obj, message_obj=message_obj)


@app.route("/employee_setting", methods=['GET', 'POST'])
def employee_setting():
    language = 'en'
    return render_template("employee_setting.html", title='Employee Settings',
                           language=language,
                           translation=translation_obj, message_obj=message_obj)


@app.route("/load_districts", methods=['GET', 'POST'])
def load_districts():
    province = request.args.get("province")
    districts = {district.id: district.district_name + "/" + district.district_name_english for district in
                 Districts.query.filter_by(province=province).all()}
    return jsonify(districts)

# @app.route("/employee_list", methods=['GET', 'POST'])
# def employee_list():
#     language = 'en'
#     add_employee_form = EmployeeForm()
#     add_employee_contact_form = EmployeeContactForm()
#     if request.method == 'POST':
#         if add_employee_form.validate_on_submit():
#             new_employee = Employees(
#                 id=add_employee_form.employee_id.data,
#                 name=add_employee_form.first_name.data,
#                 lname=add_employee_form.last_name.data,
#                 fname=add_employee_form.father_name.data,
#                 gname=add_employee_form.grand_name.data,
#                 name_english=add_employee_form.first_name_english.data,
#                 lname_english=add_employee_form.last_name_english.data,
#                 fname_english=add_employee_form.father_name_english.data,
#                 gname_english=add_employee_form.grand_name_english.data,
#                 birthday=add_employee_form.birthday.data,
#                 tazkira=add_employee_form.tazkira.data,
#                 gender=True if add_employee_form.gender.data else False,
#                 blood=add_employee_form.blood.data,
#                 m_status=True if add_employee_form.m_status.data else False,
#                 tin=add_employee_form.tin.data,
#                 status=1)
#             try:
#                 db.session.add(new_employee)
#                 db.session.commit()
#             except IOError as exc:
#                 return jsonify({'success': False, 'message': message_obj.create_new_employee_not[language]}), \
#                        403, {'ContentType': 'application/json'}
#             return jsonify({'success': True, 'message':
#                 message_obj.create_new_employee_save[language].format(add_employee_form.employee_id.data)}), \
#                    200, {'ContentType': 'application/json'}
#         elif add_employee_contact_form.validate_on_submit():
#             permanent_address = Permanent_addresses(emp_id=add_employee_contact_form.employee_id.data,
#                                               address=add_employee_contact_form.permanent_address.data,
#                                               district_id=add_employee_contact_form.district.data,
#                                               province_id=add_employee_contact_form.province.data
#                                               )
#             current_address = Current_addresses(emp_id=add_employee_contact_form.employee_id.data,
#                                               address=add_employee_contact_form.current_address.data,
#                                               district_id=add_employee_contact_form.district.data,
#                                               province_id=add_employee_contact_form.province.data
#                                               )
#             try:
#                 db.session.add(permanent_address)
#                 db.session.add(current_address)
#                 db.session.commit()
#             except IOError as exc:
#                 return jsonify({'success': False, 'message': message_obj.contact_details_not[language]}), \
#                        403, {'ContentType': 'application/json'}
#             return jsonify({'success': True, 'message': message_obj.contact_details[language]}), \
#                    200, {'ContentType': 'application/json'}
#         else:
#             return jsonify({'success': False, 'message': add_employee_form.errors}), \
#                    403, {'ContentType': 'application/json'}

#     add_employee_form = update_messages_employee(add_employee_form, language)
#     return render_template('employee_list.html', title='Add Employee',
#                            form=add_employee_form, language=language,
#                            translation=translation_obj, message_obj=message_obj, form_contact=add_employee_contact_form)
