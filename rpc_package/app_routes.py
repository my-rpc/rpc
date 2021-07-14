from flask import render_template, url_for, redirect, request, jsonify
from rpc_package import app, pass_crypt, db
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm
from rpc_package.form_dynamic_language import *
from rpc_package.rpc_tables import Users, Employees, User_roles, Permanent_addresses, Current_addresses, Emails, Phone
import json


@app.route("/", methods=['GET', 'POST'])
def blank():
    return render_template('blank.html', language='en', translation=translation_obj)


@app.route("/create_new_user", methods=['GET', 'POST'])
def create_new_user():
    language = 'en'
    # language = json.loads(request.args["messages"])['language']
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
                return jsonify({'success': False, 'message': message_obj.create_new_user_not[language]}), \
                       403, {'ContentType': 'application/json'}
            return jsonify({'success': True, 'message':
                message_obj.create_new_user_save[language].format(create_new_user_form.employee_id.data)}), \
                   200, {'ContentType': 'application/json'}
        else:
            return jsonify({'success': False, 'message': create_new_user_form.errors}), \
                   403, {'ContentType': 'application/json'}
    create_new_user_form = update_messages_user(create_new_user_form, language)
    return render_template('create_new_user.html', title='Create New User',
                           form=create_new_user_form, language=language, translation=translation_obj,
                           message_obj=message_obj)


@app.route("/uds_user", methods=['GET', 'POST'])
def uds_user():
    language = 'en'
    # language = json.loads(request.args["messages"])['language']
    create_new_user_form = CreateUserForm()
    if request.method == 'POST':
        if create_new_user_form.validate_on_submit():
            hashed_pass = pass_crypt.generate_password_hash(create_new_user_form.password.data).decode('utf=8')
            new_user = Users(emp_id=create_new_user_form.employee_id.data,
                             password=hashed_pass,
                             role=create_new_user_form.user_role.data,
                             status=1,
                             token='adding new token')
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True, 'message':
                message_obj.create_new_user_save[language].format(create_new_user_form.employee_id.data)}), \
                   200, {'ContentType': 'application/json'}
        else:
            return jsonify({'success': False, 'message': create_new_user_form.errors}), \
                   403, {'ContentType': 'application/json'}
    create_new_user_form = update_messages_user(create_new_user_form, language)
    return render_template('create_new_user.html', title='Create New User',
                           form=create_new_user_form, language=language, translation=translation_obj,
                           message_obj=message_obj)


@app.route("/login", methods=['GET', 'POST'])
def login():
    default_language = 'en'
    login_form = LoginForm()
    if login_form.validate_on_submit():
        logged_user = Users.query.filter_by(email=login_form.email.data).first()
        if logged_user and pass_crypt.check_password_hash(logged_user.password, login_form.password.data):
            pass
        if login_form.prefer_language.data and login_form.username.data == 'rpc':
            return redirect(
                url_for("create_new_user", messages=json.dumps({"language": login_form.prefer_language.data})))
    else:
        print("Check the username and password")

    return render_template('login.html', title='Login',
                           form=login_form, language=default_language,
                           translation=translation_obj, message_obj=message_obj)


@app.route("/add_employee", methods=['GET', 'POST'])
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
            permanent_address = Permanent_addresses(
                emp_id=add_employee_form.employee_id.data,
                address=add_employee_form.permanent_address.data,
                district_id=add_employee_form.district.data,
                province_id=add_employee_form.provinces.data)
            current_address = Current_addresses(
                emp_id=add_employee_form.employee_id.data,
                address=add_employee_form.current_address.data,
                district_id=add_employee_form.district.data,
                province_id=add_employee_form.provinces.data)
            email = Emails(
                emp_id=add_employee_form.employee_id.data,
                email=add_employee_form.email.data)
            # phone = Phone(
            #     emp_id=add_employee_form.employee_id.data,
            #     phone=add_employee_form.phone.data)
            try:
                db.session.add(new_employee)
                db.session.add(permanent_address)
                db.session.add(current_address)
                db.session.add(email)
                # db.session.add(phone)
                db.session.commit()
            except IOError as exc:
                return jsonify({'success': False, 'message': message_obj.create_new_employee_not[language]}), \
                       403, {'ContentType': 'application/json'}
            return jsonify({'success': True, 'message':
                message_obj.create_new_employee_save[language].format(add_employee_form.employee_id.data)}), \
                   200, {'ContentType': 'application/json'}
        else:
            return jsonify({'success': False, 'message': add_employee_form.errors}), \
                   403, {'ContentType': 'application/json'}

    add_employee_form = update_messages_employee(add_employee_form, language)
    return render_template('add_employee.html', title='Add Employee',
                           form=add_employee_form, language=language,
                           translation=translation_obj, message_obj=message_obj)


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

