from flask import render_template, url_for, redirect, request, jsonify, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from rpc_package import app, pass_crypt, db
from werkzeug.utils import secure_filename
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm, UploadCVForm, UploadGuarantorForm, \
    UploadEducationalDocsForm, \
    UploadTinForm, UploadTazkiraForm, UploadExtraDocsForm, leaveRequestForm, OvertimeRequestForm
from rpc_package.form_dynamic_language import *
from rpc_package.rpc_tables import Users, Employees, Documents, User_roles, Permanent_addresses, Current_addresses, \
    Districts, \
    Emails, Phone, Provinces, Leave_form, Overtime_form
from rpc_package.utils import EmployeeValidator, message_to_client_403, message_to_client_200
from rpc_package.route_utils import upload_docs, get_profile_info, get_documents, upload_profile_pic, \
    update_employee_data, \
    set_emp_update_form_data, send_leave_request, add_overtime_request
import os
from datetime import datetime


@app.route("/", methods=['GET', 'POST'])
@login_required
def blank():
    return render_template('blank.html', language='en', translation=translation_obj)


@app.route("/create_new_user", methods=['GET', 'POST'])
@login_required
def create_new_user():
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
                return message_to_client_403(message_obj.create_new_user_not[session['language']])
            return message_to_client_200(
                message_obj.create_new_user_save[session['language']].format(create_new_user_form.employee_id.data))
        else:
            return message_to_client_403(create_new_user_form.errors)
    users = db.session.query(Users,
                             User_roles,
                             Employees).join(Users,
                                             (Users.role == User_roles.id)).join(Employees,
                                                                                 (Users.emp_id == Employees.id)).all()

    create_new_user_form = update_messages_user(create_new_user_form, session['language'])
    return render_template('create_new_user.html', title='Create New User', users=users,
                           form=create_new_user_form, language=session['language'], translation=translation_obj,
                           message_obj=message_obj)


@app.route("/uds_user", methods=['GET', 'POST'])
@login_required
def uds_user():
    language = session['language']
    if request.method == 'POST':
        if EmployeeValidator.emp_id_validator(request.form['employee_id']) and \
                EmployeeValidator.number_validator(request.form['user_role']):
            user = Users.query.get(request.form['employee_id'])
            try:
                user.status = bool(int(request.form['status']))
                user.role = request.form['user_role']
                user_role = User_roles.query.get(user.role)
                db.session.commit()
            except IOError as exc:
                return message_to_client_403(message_obj.create_new_user_update_not[language])
            data = {
                "user": {
                    'emp_id': user.emp_id, 'status': user.status,
                    'role': {'name': user_role.name, 'name_english': user_role.name_english}
                },
                'message': message_obj.create_new_user_update[language].format(request.form['employee_id'])
            }
            return jsonify(data)
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
        return message_to_client_403(message_obj.invalid_message[language])


@app.route("/reset_user_password")
def reset_user_password():
    user_id = request.args.get('user_id')
    if EmployeeValidator.emp_id_validator(user_id):
        hashed_pass = pass_crypt.generate_password_hash('123456').decode('utf=8')
        try:
            sel_user = Users.query.get(user_id)
            sel_user.password = hashed_pass
            db.session.commit()
        except IOError as exc:
            return message_to_client_403(message_obj.create_new_user_update_not[session['language']])
        return message_to_client_200("Password has been reset")
    else:
        return message_to_client_403(message_obj.invalid_message[session['language']])


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Login part
@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            user = Users.query.filter_by(emp_id=login_form.username.data).first()
            if user and pass_crypt.check_password_hash(user.password, login_form.password.data):
                session['language'] = login_form.prefer_language.data
                login_user(user, remember=login_form.remember_me.data)
                request_user_page = request.args.get('next')
                if request_user_page:
                    return redirect(request_user_page)
                else:
                    return redirect(url_for("profile"))
            else:
                flash(message_obj.password_incorrect[session['language']], 'error')
                return redirect(url_for('login'))

    return render_template('login.html', title='Login',
                           form=login_form, language='en',
                           translation=translation_obj, message_obj=message_obj)


@app.route("/add_employee", methods=['GET', 'POST'])
@login_required
def add_employee():
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
                return message_to_client_403(message_obj.create_new_employee_not[session['language']])
            return message_to_client_200(
                message_obj.create_new_employee_save[session['language']].format(add_employee_form.employee_id.data))
        else:
            return message_to_client_403(add_employee_form.errors)

    add_employee_form = update_messages_employee(add_employee_form, session['language'])
    return render_template('add_employee.html', title='Add Employee',
                           form=add_employee_form, language=session['language'],
                           translation=translation_obj, message_obj=message_obj)


@app.route("/add_documents", methods=['GET', 'POST'])
@login_required
def add_documents():
    cv_form = UploadCVForm()
    guarantor = UploadGuarantorForm()
    education = UploadEducationalDocsForm()
    tin = UploadTinForm()
    tazkira = UploadTazkiraForm()
    extra_docs = UploadExtraDocsForm()
    emp_id = request.args.get("emp_id")

    if request.method == "GET":
        cv_doc, guarantor_doc, tin_doc, education_doc, extra_doc, tazkira_doc = get_documents(emp_id)

    if request.method == 'POST':
        if guarantor.flag.data == "guarantor":
            result = upload_docs(emp_id, request, 'guarantor')
        if cv_form.flag.data == "cv":
            result = upload_docs(emp_id, request, 'cv')
        if education and education.flag.data == "education":
            result = upload_docs(emp_id, request, 'education')
        if tin and tin.flag.data == "tin":
            result = upload_docs(emp_id, request, 'tin')
        if tazkira and tazkira.flag.data == "tazkira":
            result = upload_docs(emp_id, request, 'tazkira')
        if extra_docs and extra_docs.flag.data == "extra_docs":
            result = upload_docs(emp_id, request, 'extra_docs')

        if result == "success":
            flash("Document uploaded", result)
        else:
            flash("Document not uploaded", result)
        return redirect(request.referrer)
    return render_template("add_documents.html", title='Add Employee Documents',
                           language=session['language'],
                           translation=translation_obj, emp_id=emp_id, extra_docs_form=extra_docs,
                           tazkira_form=tazkira, form=cv_form, tin_form=tin, education_form=education,
                           guarantor_form=guarantor, message_obj=message_obj,
                           cv_doc=cv_doc, guarantor_doc=guarantor_doc, tin_doc=tin_doc,
                           education_doc=education_doc, extra_doc=extra_doc, tazkira_doc=tazkira_doc
                           )


@app.route("/delete_document", methods=['GET'])
@login_required
def delete_document():
    emp_id = request.args.get("emp_id")
    doc = request.args.get("doc")
    document = Documents.query.filter_by(emp_id=emp_id, name=doc).first()
    try:
        os.remove(os.path.join(f"./rpc_package" + document.url))
        Documents.query.filter_by(emp_id=emp_id, name=doc).delete()
        db.session.commit()
        flash("Document deleted", "success")
    except:
        flash("Document not deleted", "error")
    return redirect(request.referrer)


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
    employees = db.session.query(Employees).all()
    phones = {}
    emails = {}
    for x, emp in enumerate(employees):
        phone = db.session.query(Phone).filter_by(emp_id=emp.id).all()
        email = db.session.query(Emails).filter_by(emp_id=emp.id).all()
        if phone is not None:
            phones[x] = phone
        if email is not None:
            emails[x] = email

    return render_template("employee_settings.html", title='Employee Settings',
                           employees=employees, emails=emails, phones=phones, language=session['language'],
                           translation=translation_obj, message_obj=message_obj)


@app.route('/employee_details', methods=['GET', "POST"])
@login_required
def employee_details():
    emp_id = request.args.get('emp_id')

    if EmployeeValidator.emp_id_validator(emp_id):
        try:
            sel_emp = Employees.query.get(emp_id)
            phones = db.session.query(Phone).filter_by(emp_id=emp_id).all()
            emails = db.session.query(Emails).filter_by(emp_id=emp_id).all()

            current_addresses = db.session.query(Current_addresses, Provinces, Districts).join(Provinces,
                                                                                               (
                                                                                                           Current_addresses.province_id == Provinces.id)) \
                .join(Districts, (Current_addresses.district_id == Districts.id)) \
                .filter(Current_addresses.emp_id == emp_id).first()

            permanent_addresses = db.session.query(Permanent_addresses, Provinces, Districts).join(Provinces,
                                                                                                   (
                                                                                                               Permanent_addresses.province_id == Provinces.id)) \
                .join(Districts, (Permanent_addresses.district_id == Districts.id)) \
                .filter(Permanent_addresses.emp_id == emp_id).first()
            employee = sel_emp, phones, emails, current_addresses, permanent_addresses

        except IOError as exc:
            return render_template('employee_details.html', title='Employee Details', language=session['language'],
                                   translation=translation_obj, message_obj=message_obj)
        return render_template('employee_details.html', title='Employee Details', language=session['language'],
                               employee=employee, translation=translation_obj, message_obj=message_obj)
    else:
        flash(message_obj.invalid_message[session['language']], "error")
        return render_template('employee_details.html', title='Employee Details', language=session['language'],
                               translation=translation_obj, message_obj=message_obj)


@app.route('/uds_employee', methods=['GET', "POST"])
@login_required
def uds_employee():
    language = 'en'
    update_employee_form = EmployeeForm()
    if request.method == 'POST':
        if not update_employee_form.validate_on_submit():

            for key, value in update_employee_form.errors.items():
                if value[0] != message_obj.val_dic[key][0]:
                    update_employee_form.validate_on_submit()

            try:
                update_employee_data(update_employee_form)

            except IOError as exc:
                return message_to_client_403(message_obj.create_new_employee_update_not[session['language']])
            data = {
                'employee': {
                    'emp_id': update_employee_form.employee_id.data,
                    'name': update_employee_form.first_name.data + ' ' + update_employee_form.last_name.data,
                    'name_english': update_employee_form.first_name_english.data + ' ' + update_employee_form.last_name_english.data,
                    'father_name': update_employee_form.father_name.data,
                    'father_name_english': update_employee_form.father_name_english.data,
                    'phone': update_employee_form.phone.data + '<br>' + update_employee_form.phone_second.data,
                    'email': update_employee_form.email.data + '<br>' + update_employee_form.email_second.data,
                    'gender': update_employee_form.gender.data,
                    'tazkira': update_employee_form.tazkira.data,
                    'm_status': update_employee_form.m_status.data,
                    'birthday': update_employee_form.birthday.data,
                    'blood': update_employee_form.blood.data,
                    'tin': update_employee_form.tin.data
                },
                'message': message_obj.create_new_employee_update[session['language']].format(
                    request.form['employee_id'])
            }
            return jsonify(data)
        else:
            return message_to_client_403(update_employee_form.errors)

    emp_id = request.args.get('emp_id')
    if EmployeeValidator.emp_id_validator(emp_id):
        emp_update_data = set_emp_update_form_data(emp_id, update_employee_form)

        data = jsonify(render_template('ajax_template/update_employee_form.html', language=session['language'],
                                       form=update_employee_form, translation=translation_obj, message_obj=message_obj),
                       {'current_add': emp_update_data[0], 'permanent_add': emp_update_data[1]})
        return data
    else:
        message_to_client_403(message_obj.invalid_message[session['language']])


@app.route('/delete_employee', methods=['DELETE'])
def delete_employee():
    emp_id = request.args.get('emp_id')
    if EmployeeValidator.emp_id_validator(emp_id):
        try:
            sel_emp = Employees.query.get(emp_id)
            db.session.delete(sel_emp)
            db.session.commit()
        except IOError as exc:
            return message_to_client_403(message_obj.create_new_employee_delete_not[session['language']])
        return message_to_client_200(
            message_obj.create_new_employee_delete[session['language']].format(emp_id))
    else:
        message_to_client_403(message_obj.invalid_message[session['language']])


@app.route('/profile')
@login_required
def profile():
    profile, current_address, permanent_address, doc_cv, email, phone, doc_tazkira, doc_guarantor, doc_tin, doc_education, doc_extra = get_profile_info(
        current_user.emp_id)
    return render_template('profile.html', title='My Profile', language=session['language'], profile=profile,
                           current_address=current_address,
                           permanent_address=permanent_address, doc_cv=doc_cv, email=email, phone=phone,
                           doc_tazkira=doc_tazkira,
                           doc_guarantor=doc_guarantor, doc_tin=doc_tin, doc_education=doc_education,
                           doc_extra=doc_extra,
                           translation=translation_obj, message_obj=message_obj)


@app.route('/upload_profile_pic', methods=["POST"])
@login_required
def upload_profile():
    return upload_profile_pic(request)


@app.route('/leave_request', methods=["GET", "POST"])
@login_required
def leave_request():
    leave_form = leaveRequestForm()
    if request.method == "GET":
        my_leave_list = Leave_form.query.filter_by(emp_id=current_user.emp_id).all()
    if request.method == 'POST':
        if leave_form.validate_on_submit():
            leave = send_leave_request(leave_form, current_user.emp_id)
            if leave == "success":
                flash(message_obj.leave_request_sent[session['language']], 'success')
            else:
                flash(message_obj.leave_request_not_sent[session['language']], 'error')
        else:
            flash(leave_form.errors)
        return redirect(url_for('leave_request'))
    return render_template('leave_request.html', form=leave_form, my_leave_list=my_leave_list,
                           title=translation_obj.forms[session['language']], language=session['language'],
                           translation=translation_obj, message_obj=message_obj)

@app.route('/overtime_request', methods=["GET", "POST"])
@login_required
def overtime_request():
    overtime_form = OvertimeRequestForm()
    if request.method == "GET":
        emp_overtime_list = Overtime_form.query \
            .filter_by(emp_id=current_user.emp_id) \
            .order_by(Overtime_form.requested_at.desc()).all()
    if request.method == 'POST':
        if overtime_form.validate_on_submit():
            overtime = add_overtime_request(overtime_form, current_user.emp_id)
            if overtime == "success":
                flash(message_obj.overtime_request_sent[session['language']], 'success')
            else:
                flash(message_obj.overtime_request_not_sent[session['language']], 'error')
        else:
            flash(overtime_form.errors)
        return redirect(url_for('overtime_request'))
    return render_template('overtime_request.html', form=overtime_form, emp_overtime_list=emp_overtime_list,
                           title=translation_obj.forms[session['language']], language=session['language'],
                           translation=translation_obj, message_obj=message_obj)
