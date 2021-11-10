from flask import render_template, url_for, redirect, request, jsonify, flash, session, send_file
from flask_login import login_user, current_user, logout_user, login_required
from rpc_package import app, pass_crypt, db
from werkzeug.utils import secure_filename
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm, UploadCVForm, UploadGuarantorForm, \
    AddEquipmentForm, ResignRequestForm, UploadEducationalDocsForm, \
    UploadTinForm, UploadTazkiraForm, UploadExtraDocsForm, leaveRequestForm, departmentForm, OvertimeRequestForm, \
    ContractForm, LoanRequestForm, LoanGuarantorForm, LoanHRForm, LoanPresidencyForm, LoanFinanceForm, AcceptEquipmentForm, \
    OvertimeSupervisorForm, OvertimeHRForm, LeaveSupervisorForm, LeaveHRForm, HolidayForm, AttendanceForm, ChangePassForm, \
    EquipmentForm, AssignEquipmentForm, SurrenderEquipmentForm

from rpc_package.form_dynamic_language import *

from rpc_package.rpc_tables import Users, Employees, Documents, User_roles, Permanent_addresses, Current_addresses, \
    Contracts, Contract_types, Positions, Position_history, Salary, Employee_equipment, \
    Departments, Overtime_form, Districts, Equipment, Resign_form, Emails, Phone, Provinces, Leave_form, \
    Loan_form, Overtime_reason, Leave_reason, Holiday, AttendanceFile, Equipment, Notification
from rpc_package.utils import EmployeeValidator, message_to_client_403, message_to_client_200, \
    to_gregorian, to_jalali, check_access, get_last_date_of_month
from rpc_package.route_utils import upload_docs, get_profile_info, get_documents, upload_profile_pic, \
    add_contract_form, add_overtime_request, set_contact_update_form_data, update_contract, assign_equipment, \
    send_resign_request, update_employee_data, set_emp_update_form_data, add_leave_request, \
    send_resign_request, send_department, add_loan_request, accept_equipment, accept_reject_resign, \
    add_holiday, add_attendance, add_new_equipment, add_employee_equipment, surrender_equipment_update, \
    push_notification, get_role_ids
import os
import datetime
import jdatetime
from sqlalchemy import func
from rpc_package.attendance import Attendance

@app.before_request
def check_contract():
    if current_user.is_authenticated:
        position_history = current_user.employee.position_history.filter_by(status=1).first()
        if not position_history and current_user.user_role.name_english != 'Admin':
            logout_user()

@app.route("/create_new_user", methods=['GET', 'POST'])
@login_required
def create_new_user():
    if not check_access('create_new_user'):
        return redirect(url_for('access_denied'))
    create_new_user_form = CreateUserForm(session['language'])
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
                db.session.flush()
                db.session.commit()
            except IOError as exc:
                return message_to_client_403(message_obj.create_new_user_not[session['language']])
            data = {
                "user": {
                    'emp_id': new_user.emp_id,
                    'status': translation_obj.active[session['language']] if new_user.status else translation_obj.inactive[session['language']],
                    'name' : '{} {}'.format(new_user.employee.name_english, new_user.employee.lname_english) if session['language'] == 'en' else '{} {}'.format(new_user.employee.name, new_user.employee.lname),
                    'role': new_user.user_role.name if session['language'] == 'dari' else new_user.user_role.name_english
                },
                'message': message_obj.create_new_user_save[session['language']].format(create_new_user_form.employee_id.data)
            }
            return jsonify(data)
        else:
            return message_to_client_403(create_new_user_form.errors)
    users = db.session.query(Users,
                             User_roles,
                             Employees).join(Users,
                                             (Users.role == User_roles.id)).join(Employees,
                                                                                 (Users.emp_id == Employees.id)).all()
    return render_template('create_new_user.html', title='Create New User', users=users,
                           form=create_new_user_form, language=session['language'],                            )


@app.route("/uds_user", methods=['GET', 'POST'])
@login_required
def uds_user():
    if not check_access('uds_user'):
        return redirect(url_for('access_denied'))
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
                    'emp_id': user.emp_id, 'status': translation_obj.active[session['language']] if user.status else translation_obj.inactive[session['language']],
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
    if not check_access('reset_user_password'):
        return redirect(url_for('access_denied'))
    user_id = request.args.get('user_id')
    if EmployeeValidator.emp_id_validator(user_id):
        hashed_pass = pass_crypt.generate_password_hash('123456').decode('utf=8')
        try:
            sel_user = Users.query.get(user_id)
            sel_user.password = hashed_pass
            db.session.commit()
            # Notification Generate and save in table
            notify_ms = notification_msg.reset_user_password
            push_notification(sel_user.emp_id, notify_ms, notify_ms['url'])
        except IOError as exc:
            return message_to_client_403(message_obj.create_new_user_update_not[session['language']])
        return message_to_client_200("Password has been reset")
    else:
        return message_to_client_403(message_obj.invalid_message[session['language']])


@app.route("/logout")
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
    if login_form.validate_on_submit():
        user = Users.query.filter_by(emp_id=login_form.username.data).first()
        if user and pass_crypt.check_password_hash(user.password, login_form.password.data):
            position_history = user.employee.position_history.filter_by(status=1).first()
            if (user.status and position_history) or user.user_role.name_english == 'Admin':
                employee = Employees.query.filter_by(id=user.emp_id).first()
                session['language'] = login_form.prefer_language.data
                session['emp_id'] = user.emp_id
                if session['language'] == 'dari':
                    session['emp_name'] = employee.name
                    session['emp_lname'] = employee.lname
                else:
                    session['emp_name'] = employee.name_english
                    session['emp_lname'] = employee.lname_english
                login_user(user, remember=login_form.remember_me.data)
                request_user_page = request.args.get('next')
                if request_user_page:
                    return redirect(request_user_page)
                else:
                    return redirect('/profile')
            else:
                flash(message_obj.user_inactive[session['language']], 'error')
                return redirect(request.referrer)
        else:
            flash(message_obj.password_incorrect[session['language']], 'error')
            return redirect(request.referrer)

    return render_template('login.html', title='Login', form=login_form, language='en')


@app.route("/add_employee", methods=['GET', 'POST'])
@login_required
def add_employee():
    if not check_access('add_employee'):
        return redirect(url_for('access_denied'))
    add_employee_form = EmployeeForm(session['language'])
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
                birthday=to_gregorian(add_employee_form.birthday.data),
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

    return render_template('add_employee.html', title='Add Employee',
                form=add_employee_form, language=session['language'])


@app.route("/add_documents", methods=['GET', 'POST'])
@login_required
def add_documents():
    if not check_access('add_documents'):
        return redirect(url_for('access_denied'))
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
                        emp_id=emp_id, extra_docs_form=extra_docs,
                           tazkira_form=tazkira, form=cv_form, tin_form=tin, education_form=education,
                           guarantor_form=guarantor,
                           cv_doc=cv_doc, guarantor_doc=guarantor_doc, tin_doc=tin_doc,
                           education_doc=education_doc, extra_doc=extra_doc, tazkira_doc=tazkira_doc)


@app.route("/delete_document", methods=['GET'])
@login_required
def delete_document():
    if not check_access('delete_document'):
        return redirect(url_for('access_denied'))
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
    if not check_access('load_districts'):
        return redirect(url_for('access_denied'))
    if request.method == "POST":
        province = request.args.get("province")
        districts = {district.id: district.district_name + "/" + district.district_name_english for district in
                     Districts.query.filter_by(province=province).all()}
        return jsonify(districts)


@app.route("/employee_settings", methods=['GET', 'POST'])
@login_required
def employee_settings():
    if not check_access('employee_settings'):
        return redirect(url_for('access_denied'))
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
            employees=employees, emails=emails, phones=phones, language=session['language'])


@app.route('/employee_details', methods=['GET', "POST"])
@login_required
def employee_details():
    if not check_access('employee_details'):
        return redirect(url_for('access_denied'))
    emp_id = request.args.get('emp_id')

    if EmployeeValidator.emp_id_validator(emp_id):
        try:
            employee = Employees.query.filter_by(id=emp_id).first()
        except IOError as exc:
            return render_template('employee_details.html', title='Employee Details', language=session['language'])

        return render_template('employee_details.html', title='Employee Details', language=session['language'], employee=employee, Position_history=Position_history)
    else:
        flash(message_obj.invalid_message[session['language']], "error")
        return render_template('employee_details.html', title='Employee Details', language=session['language'])


@app.route('/uds_employee', methods=['GET', "POST"])
@login_required
def uds_employee():
    if not check_access('uds_employee'):
        return redirect(url_for('access_denied'))
    update_employee_form = EmployeeForm(session['language'])
    if request.method == 'POST':
        ignored_items = False
        if not update_employee_form.validate_on_submit():
            for key, value in update_employee_form.errors.items():
                if key not in message_obj.val_dic.keys():
                    ignored_items = True
                    break
        if ignored_items:
            return message_to_client_403(update_employee_form.errors)
        else:
            try:
                # TODO Phone and Email for duplicate validation and conflict
                update_employee_data(update_employee_form)

            except IOError as exc:
                return message_to_client_403(message_obj.create_new_employee_update_not[session['language']])
            data = {
                'employee': {
                    'emp_id': update_employee_form.employee_id.data,
                    'name': update_employee_form.first_name.data + ' ' + update_employee_form.last_name.data
                    if session['language'] == 'dari'
                    else update_employee_form.first_name_english.data + ' ' + update_employee_form.last_name_english.data,
                    'father_name': update_employee_form.father_name.data
                    if session['language'] == 'dari'
                    else update_employee_form.father_name_english.data,
                    'phone': update_employee_form.phone.data + '<br>' + update_employee_form.phone_second.data,
                    'email': update_employee_form.email.data + '<br>' + update_employee_form.email_second.data,
                    'gender': translation_obj.male[session['language']] if update_employee_form.gender.data == '1' else translation_obj.female[session['language']],
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


    emp_id = request.args.get('emp_id')
    if EmployeeValidator.emp_id_validator(emp_id):
        emp_update_data = set_emp_update_form_data(emp_id, update_employee_form)

        data = jsonify(render_template('ajax_template/update_employee_form.html', language=session['language'],
                                       form=update_employee_form, ),
                       {'current_add': emp_update_data[0], 'permanent_add': emp_update_data[1]})
        return data
    else:
        message_to_client_403(message_obj.invalid_message[session['language']])


@app.route('/delete_employee', methods=['DELETE'])
@login_required
def delete_employee():
    if not check_access('delete_employee'):
        return redirect(url_for('access_denied'))
    emp_id = request.args.get('emp_id')
    if EmployeeValidator.emp_id_validator(emp_id):
        try:
            sel_emp = Employees.query.get(emp_id)
            for email in sel_emp.emails:
                db.session.delete(email)
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
    if not check_access('profile'):
        return redirect(url_for('access_denied'))
    employee = Employees.query.filter_by(id=current_user.emp_id).first()
    change_pass_form = ChangePassForm(session['language'])
    return render_template('profile.html', title='My Profile', language=session['language'],
        employee=employee, Position_history=Position_history, change_pass_form=change_pass_form)

@app.route("/change_password", methods=['POST'])
@login_required
def change_password():
    if not check_access('change_password'):
        return redirect(url_for('access_denied'))
    change_pass_form = ChangePassForm(session['language'], current_user)
    if request.method == "POST":
        if change_pass_form.validate_on_submit():
            try:
                hashed_pass = pass_crypt.generate_password_hash(change_pass_form.new_pass.data).decode('utf=8')
                current_user.password = hashed_pass
                db.session.commit()
                flash(message_obj.password_changed[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.password_not_changed[session['language']], 'error')
        else:
            flash(change_pass_form.errors)
    return redirect(url_for('profile'))

@app.route('/contract_settings')
@login_required
def contract_settings():
    if not check_access('contract_settings'):
        return redirect(url_for('access_denied'))
    position_history = Position_history.query.all()
    return render_template('contract_settings.html', title='Contact Setting',
        language=session['language'], position_history=position_history)

@app.route('/add_contract', methods=["GET", "POST"])
@login_required
def add_contract():
    if not check_access('add_contract'):
        return redirect(url_for('access_denied'))
    contract_form = ContractForm(session['language'])
    emp_id = request.args.get('emp_id')
    if request.method == "POST":
        if contract_form.validate_on_submit():
            con_startdate = Position_history.query.filter_by(emp_id=contract_form.emp_id.data, status = True).first()
            # date = datetime.datetime.strptime(to_gregorian(contract_form.start_date.data), '%Y-%m-%d')
            if con_startdate:
                flash({'contract_status':[message_obj.active_contract_message[session['language']] ]}, 'error')
                return redirect(request.referrer)
            contract = add_contract_form(contract_form)
            if contract == "success":
                # Notification Generate and save in table
                notify_ms = notification_msg.add_new_contract
                push_notification(contract_form.emp_id.data, notify_ms, notify_ms['url'])
                flash(message_obj.contract_added[session['language']].format(emp_id), 'success')
                # TODO show msg to page
                return redirect(url_for('contract_settings'))
            else:
                flash(message_obj.contract_not_added[session['language']].format(emp_id), 'error')
            return redirect(request.referrer)
        else:
            flash(contract_form.errors, 'error')
            return redirect(request.referrer)
    if request.method == "GET":
        # return 'asd'
        if EmployeeValidator.emp_id_validator(emp_id):
            contract_form.emp_id.data = emp_id
            return render_template('add_contract.html', title='Add Contract',
                language=session['language'], form=contract_form)


@app.route('/edit_contract', methods=['GET', "POST"])
@login_required
def edit_contract():
    if not check_access('edit_contract'):
        return redirect(url_for('access_denied'))
    contract_form = ContractForm(session['language'])
    if request.method == "POST":
        if contract_form.validate_on_submit():
            updated_contract = update_contract(request, contract_form)

            if update_contract != 'error':
                return jsonify({
                    "contract": updated_contract,
                    'message': message_obj.contract_update[session['language']].format(request.form['emp_id'])
                })
            else:
                message_to_client_403(message_obj.contract_update_not[session['language']])
        else:
            return message_to_client_403(contract_form.errors)

    contract_id = request.args.get('contract_id')

    contract_update_data = set_contact_update_form_data(contract_id, contract_form)
    data = jsonify(render_template('ajax_template/update_contract_form.html', language=session['language'],
                form=contract_form)
                ,{"contract_type":contract_update_data[0], "position": contract_update_data[1], "department":contract_update_data[2]})
    if data == 'error':
        return 'error'
    else:
        return data



@app.route('/contract_details/<int:contract_id>', methods=['GET'])
@login_required
def contract_details(contract_id):
    if not check_access('contract_details'):
        return redirect(url_for('access_denied'))
    try:
        contract = Position_history.query.filter_by(id=contract_id).first()
    except IOError as exc:
        flash(exe, 'error')
    return render_template('contract_details.html', contract=contract, language=session['language'])

@app.route('/delete_contract', methods=['delete'])
@login_required
def delete_contract():
    if not check_access('delete_contract'):
        return redirect(url_for('access_denied'))
    try:
        sel_emp = Position_history.query.filter_by(id=request.args.get('contract_id')).first()
        db.session.delete(sel_emp.salary)
        db.session.delete(sel_emp)
        db.session.commit()
    except IOError as exc:
        return message_to_client_403(message_obj.contract_delete_not[session['language']])
    return message_to_client_200(
        message_obj.contract_delete[session['language']].format(sel_emp.emp_id))

@app.route('/change_contract_status', methods=['GET'])
@login_required
def change_contract_status():
    if not check_access('change_contract_status'):
        return redirect(url_for('access_denied'))
    try:
        position_history = Position_history.query.filter_by(id=request.args.get('contract_id')).first()
        position_history.status = not position_history.status
        db.session.commit()
    except IOError as exc:
        return message_to_client_403(message_obj.contract_delete_not[session['language']])
    status = translation_obj.active[session['language']] if position_history.status else translation_obj.inactive[session['language']]
    message = message_obj.contract_status_changed[session['language']].format(position_history.emp_id, status)
    return jsonify({'success': True, 'message': message, 'status': status}), 200, {'ContentType': 'application/json'}


@app.route('/upload_profile_pic', methods=["POST"])
@login_required
def upload_profile():
    if not check_access('upload_profile_pic'):
        return redirect(url_for('access_denied'))
    return upload_profile_pic(request)


@app.route('/leave_request', methods=["GET", "POST"])
@login_required
def leave_request():
    if not check_access('leave_request'):
        return redirect(url_for('access_denied'))
    leave_form = leaveRequestForm(session['language'])
    if request.method == "GET":
        my_leave_list = Leave_form.query \
            .filter_by(emp_id=current_user.emp_id) \
            .order_by(Leave_form.requested_at.desc()).all()
    if request.method == 'POST':
        if leave_form.validate_on_submit():
            leave = add_leave_request(leave_form, current_user.emp_id)
            if leave != "error":
                # Get the list of employee for generating the notification
                employees = db.session.query(Employees.id).join(Position_history, Position_history.emp_id == Employees.id) \
                    .join(Users, Users.emp_id == Employees.id) \
                    .filter(Position_history.department_id==current_user.department.id) \
                    .filter(Users.role.in_(get_role_ids('leave_supervisor'))) \
                    .filter(Users.status == True).all()
                # Notification Generate and save in table
                notify_ms = notification_msg.leave_request_send.copy()
                notify_ms['message'] = notify_ms['message'].format(current_user.employee.name + ' ' + current_user.employee.lname)
                notify_ms['message_english'] = notify_ms['message_english'].format(current_user.employee.name_english + ' ' + current_user.employee.lname_english)
                notify_ms['url'] = notify_ms['url'].format(leave.id)
                for emp in employees:
                    push_notification(emp.id, notify_ms, notify_ms['url'])

                flash(message_obj.leave_request_sent[session['language']], 'success')
            else:
                flash(message_obj.leave_request_not_sent[session['language']], 'error')
        else:
            flash(leave_form.errors)
        return redirect(url_for('leave_request'))
    return render_template('leave_request.html', form=leave_form, my_leave_list=my_leave_list,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route("/delete_leave/<int:leave_id>", methods=['GET'])
@login_required
def delete_leave(leave_id):
    if not check_access('delete_leave'):
        return redirect(url_for('access_denied'))
    try:
        leave = Leave_form.query.get(leave_id)
        if leave.emp_id == current_user.emp_id and leave.supervisor == None and leave.hr == None:
            db.session.delete(leave)
            db.session.commit()
            flash(message_obj.leave_request_deleted[session['language']], 'success')
        else:
            flash(message_obj.leave_request_not_deleted[session['language']], 'error')
    except IOError as exc:
        flash(message_obj.leave_request_not_deleted[session['language']], 'error')
    return redirect(url_for('leave_request'))   

@app.route('/leave_supervisor', methods=["GET"])
@login_required
def leave_supervisor():
    if not check_access('leave_supervisor'):
        return redirect(url_for('access_denied'))
    page = request.args.get('page') if request.args.get('page') else 1
    emps = db.session.query(Position_history.emp_id).filter(Position_history.department_id == current_user.department.id).distinct()
    
    leave_supervisor = Leave_form.query \
        .filter(Leave_form.emp_id.in_(emps)) \
        .order_by(Leave_form.requested_at.desc()) \
        .paginate(per_page=10,page=int(page),error_out=True)
    return render_template('leave_supervisor.html', leave_supervisor=leave_supervisor,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/leave_supervisor/<int:leave_id>', methods=["GET", "POST"])
@login_required
def leave_supervisor_view(leave_id):
    if not check_access('leave_supervisor'):
        return redirect(url_for('access_denied'))
    leave_supervisor_form = LeaveSupervisorForm(session['language'])
    if request.method == "GET":
        leave_data = Leave_form.query \
            .filter_by(id=leave_id).first()
    if request.method == 'POST':
        if leave_supervisor_form.validate_on_submit():
            try:
                leave_form = Leave_form.query.get(leave_id)
                leave_form.supervisor = bool(int(request.form['supervisor']))
                leave_form.supervisor_id = current_user.emp_id
                leave_form.finalized_at=datetime.datetime.now()
                if request.form['supervisor'] == '0':
                    leave_reason = Leave_reason(
                        leave_id = leave_form.id,
                        reason = request.form['reason']
                    )
                    db.session.add(leave_reason)
                db.session.commit()
                # Notification Generate and save in table
                notify_ms = notification_msg.supervisor_leave_request_employee.copy()
                notify_ms['message'] = notify_ms['message'].format('تایید کرده' if request.form['supervisor'] == '1' else 'رد کرده')
                notify_ms['message_english'] = notify_ms['message_english'].format('accepted' if request.form['supervisor'] == '1' else 'rejected')
                push_notification(leave_form.employee.id, notify_ms, notify_ms['url'])
                if request.form['supervisor'] == '0':
                    flash(message_obj.leave_request_rejected[session['language']], 'success')
                else:
                    # Get the list of employee for generating the notification for all user have access in leave_hr route
                    users = db.session.query(Users.emp_id).join(User_roles, User_roles.id == Users.role) \
                        .filter(Users.role.in_(get_role_ids('leave_hr'))) \
                        .filter(Users.status == True).all()
                    # Notification Generate and save in table
                    notify_ms = notification_msg.supervisor_leave_request_hr.copy()
                    notify_ms['message'] = notify_ms['message'].format(leave_form.employee.name + ' ' + leave_form.employee.lname)
                    notify_ms['message_english'] = notify_ms['message_english'].format(leave_form.employee.name_english + ' ' + leave_form.employee.lname_english)
                    notify_ms['url'] = notify_ms['url'].format(leave_form.id)
                    for user in users:
                        push_notification(user.emp_id, notify_ms, notify_ms['url'])
                    flash(message_obj.leave_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(exe, 'error')
        else:
            flash(leave_supervisor_form.errors)
            return redirect(url_for('leave_supervisor_view', leave_id=leave_id))
        return redirect(url_for('leave_supervisor'))
    return render_template('leave_supervisor_view.html', form=leave_supervisor_form, leave_data=leave_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/leave_hr', methods=["GET"])
@login_required
def leave_hr():
    if not check_access('leave_hr'):
        return redirect(url_for('access_denied'))
    page = request.args.get('page') if request.args.get('page') else 1
    leave_hr = Leave_form.query \
        .filter_by(supervisor = 1) \
        .order_by(Leave_form.requested_at.desc()) \
        .paginate(per_page=10,page=int(page),error_out=True)
    return render_template('leave_hr.html', leave_hr=leave_hr,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/leave_hr/<int:leave_id>', methods=["GET", "POST"])
@login_required
def leave_hr_view(leave_id):
    if not check_access('leave_hr'):
        return redirect(url_for('access_denied'))
    leave_hr_form = LeaveHRForm(session['language'])
    if request.method == "GET":
        leave_data = Leave_form.query \
            .filter_by(id=leave_id).first()
    if request.method == 'POST':
        if leave_hr_form.validate_on_submit():
            try:
                leave_form = Leave_form.query.get(leave_id)
                leave_form.hr = bool(int(request.form['hr']))
                leave_form.hr_id = current_user.emp_id
                leave_form.finalized_at=datetime.datetime.now()
                db.session.commit()
                # Notification Generate and save in table
                notify_ms = notification_msg.hr_leave_request_employee.copy()
                notify_ms['message'] = notify_ms['message'].format('تایید کرده' if request.form['hr'] == '1' else 'رد کرده')
                notify_ms['message_english'] = notify_ms['message_english'].format('accepted' if request.form['hr'] == '1' else 'rejected')
                push_notification(leave_form.employee.id, notify_ms, notify_ms['url'])
                if request.form['hr'] == '0':
                    flash(message_obj.leave_request_rejected[session['language']], 'success')
                else:
                    flash(message_obj.leave_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(exe, 'error')
        else:
            flash(leave_hr_form.errors)
        return redirect(url_for('leave_hr'))
    return render_template('leave_hr_view.html', form=leave_hr_form, leave_data=leave_data,
        title=translation_obj.forms[session['language']], language=session['language'])
@app.route('/leave_report', methods=["GET"])
@login_required
def leave_report():
    if not check_access('leave_report'):
        return redirect(url_for('access_denied'))
    leave_report = []
    if (request.args.get('from') and request.args.get('to')):
        leave_report = Employees.query.join(Employees.leaves, aliased=True) \
            .filter_by(hr=1) \
            .filter(Leave_form.start_datetime >= to_gregorian(request.args.get('from'))) \
            .filter(Leave_form.start_datetime < to_gregorian(request.args.get('to'))).all()

    return render_template('leave_report.html', leave_report=leave_report,
        title=translation_obj.forms[session['language']], language=session['language'],
        Leave_form=Leave_form, request=request)

@app.route('/overtime_request', methods=["GET", "POST"])
@login_required
def overtime_request():
    if not check_access('overtime_request'):
        return redirect(url_for('access_denied'))
    overtime_form = OvertimeRequestForm(session['language'])
    if request.method == "GET":
        emp_overtime_list = Overtime_form.query \
            .filter_by(emp_id=current_user.emp_id) \
            .order_by(Overtime_form.requested_at.desc()).all()
    if request.method == 'POST':
        if overtime_form.validate_on_submit():
            overtime = add_overtime_request(overtime_form, current_user.emp_id)
            if overtime != "error":
                # Get the list of employee for generating the notification
                employees = db.session.query(Employees.id).join(Position_history, Position_history.emp_id == Employees.id) \
                    .join(Users, Users.emp_id == Employees.id) \
                    .filter(Position_history.department_id==current_user.department.id) \
                    .filter(Users.role.in_(get_role_ids('overtime_supervisor'))) \
                    .filter(Users.status == True).all()
                # Notification Generate and save in table
                notify_ms = notification_msg.overtime_request_send.copy()
                notify_ms['message'] = notify_ms['message'].format(current_user.employee.name + ' ' + current_user.employee.lname)
                notify_ms['message_english'] = notify_ms['message_english'].format(current_user.employee.name_english + ' ' + current_user.employee.lname_english)
                notify_ms['url'] = notify_ms['url'].format(overtime.id)
                for emp in employees:
                    push_notification(emp.id, notify_ms, notify_ms['url'])

                flash(message_obj.overtime_request_sent[session['language']], 'success')
            else:
                flash(message_obj.overtime_request_not_sent[session['language']], 'error')
        else:
            flash(overtime_form.errors)
        return redirect(url_for('overtime_request'))
    return render_template('overtime_request.html', form=overtime_form, emp_overtime_list=emp_overtime_list,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route("/delete_overtime/<int:overtime_id>", methods=['GET'])
@login_required
def delete_overtime(overtime_id):
    if not check_access('delete_overtime'):
        return redirect(url_for('access_denied'))
    try:
        overtime = Overtime_form.query.get(overtime_id)
        if overtime.emp_id == current_user.emp_id and overtime.supervisor == None and overtime.hr == None:
            db.session.delete(overtime)
            db.session.commit()
            flash(message_obj.overtime_request_deleted[session['language']], 'success')
        else:
            flash(message_obj.overtime_request_not_deleted[session['language']], 'error')
    except IOError as exc:
        flash(message_obj.overtime_request_not_deleted[session['language']], 'error')
    return redirect(url_for('overtime_request'))

@app.route('/overtime_supervisor', methods=["GET"])
@login_required
def overtime_supervisor():
    if not check_access('overtime_supervisor'):
        return redirect(url_for('access_denied'))
    page = request.args.get('page') if request.args.get('page') else 1
    emps = db.session.query(Position_history.emp_id).filter(Position_history.department_id == current_user.department.id).distinct()
    overtime_supervisor = Overtime_form.query \
        .filter(Overtime_form.emp_id.in_(emps)) \
        .order_by(Overtime_form.requested_at.desc()) \
        .paginate(per_page=10,page=int(page),error_out=True)
    return render_template('overtime_supervisor.html', overtime_supervisor=overtime_supervisor,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/overtime_supervisor/<int:overtime_id>', methods=["GET", "POST"])
@login_required
def overtime_supervisor_view(overtime_id):
    if not check_access('overtime_supervisor'):
        return redirect(url_for('access_denied'))
    overtime_supervisor_form = OvertimeSupervisorForm(session['language'])
    if request.method == "GET":
        overtime_data = Overtime_form.query \
            .filter_by(id=overtime_id).first()
    if request.method == 'POST':
        if overtime_supervisor_form.validate_on_submit():
            try:
                overtime_form = Overtime_form.query.get(overtime_id)
                overtime_form.supervisor = bool(int(request.form['supervisor']))
                overtime_form.supervisor_id = current_user.emp_id
                overtime_form.finalized_at=datetime.datetime.now()
                if request.form['supervisor'] == '0':
                    overtime_reason = Overtime_reason(
                        overtime_id = overtime_form.id,
                        reason = request.form['reason']
                    )
                    db.session.add(overtime_reason)
                db.session.commit()
                # Notification Generate and save in table
                notify_ms = notification_msg.supervisor_overtime_request_employee.copy()
                notify_ms['message'] = notify_ms['message'].format('تایید کرده' if request.form['supervisor'] == '1' else 'رد کرده')
                notify_ms['message_english'] = notify_ms['message_english'].format('accepted' if request.form['supervisor'] == '1' else 'rejected')
                push_notification(overtime_form.employee.id, notify_ms, notify_ms['url'])
                if request.form['supervisor'] == '0':
                    flash(message_obj.overtime_request_rejected[session['language']], 'success')
                else:
                    # Get the list of employee for generating the notification for all user have access in overtime_hr route
                    users = db.session.query(Users.emp_id).join(User_roles, User_roles.id == Users.role) \
                        .filter(Users.role.in_(get_role_ids('overtime_hr'))) \
                        .filter(Users.status == True).all()
                    # Notification Generate and save in table
                    notify_ms = notification_msg.supervisor_overtime_request_hr.copy()
                    notify_ms['message'] = notify_ms['message'].format(overtime_form.employee.name + ' ' + overtime_form.employee.lname)
                    notify_ms['message_english'] = notify_ms['message_english'].format(overtime_form.employee.name_english + ' ' + overtime_form.employee.lname_english)
                    notify_ms['url'] = notify_ms['url'].format(overtime_form.id)
                    for user in users:
                        push_notification(user.emp_id, notify_ms, notify_ms['url'])

                    flash(message_obj.overtime_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(exc, 'error')
        else:
            flash(overtime_supervisor_form.errors)
            return redirect(url_for('overtime_supervisor_view', overtime_id=overtime_id))
        return redirect(url_for('overtime_supervisor'))
    return render_template('overtime_supervisor_view.html', form=overtime_supervisor_form, overtime_data=overtime_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/overtime_hr', methods=["GET"])
@login_required
def overtime_hr():
    if not check_access('overtime_hr'):
        return redirect(url_for('access_denied'))
    page = request.args.get('page') if request.args.get('page') else 1
    overtime_hr = Overtime_form.query \
        .filter_by(supervisor = 1) \
        .order_by(Overtime_form.requested_at.desc()) \
        .paginate(per_page=10,page=int(page),error_out=True)
    return render_template('overtime_hr.html', overtime_hr=overtime_hr,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/overtime_hr/<int:overtime_id>', methods=["GET", "POST"])
@login_required
def overtime_hr_view(overtime_id):
    if not check_access('overtime_hr'):
        return redirect(url_for('access_denied'))
    overtime_hr_form = OvertimeHRForm(session['language'])
    if request.method == "GET":
        overtime_data = Overtime_form.query \
            .filter_by(id=overtime_id).first()
    if request.method == 'POST':
        if overtime_hr_form.validate_on_submit():
            try:
                overtime_form = Overtime_form.query.get(overtime_id)
                overtime_form.hr = bool(int(request.form['hr']))
                overtime_form.hr_id = current_user.emp_id
                overtime_form.finalized_at=datetime.datetime.now()
                db.session.commit()
                # Notification Generate and save in table
                notify_ms = notification_msg.hr_overtime_request_employee.copy()
                notify_ms['message'] = notify_ms['message'].format('تایید کرده' if request.form['hr'] == '1' else 'رد کرده')
                notify_ms['message_english'] = notify_ms['message_english'].format('accepted' if request.form['hr'] == '1' else 'rejected')
                push_notification(overtime_form.employee.id, notify_ms, notify_ms['url'])
                if request.form['hr'] == '0':
                    flash(message_obj.overtime_request_rejected[session['language']], 'success')
                else:
                    flash(message_obj.overtime_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(exc, 'error')
        else:
            flash(overtime_hr_form.errors)
        return redirect(url_for('overtime_hr'))
    return render_template('overtime_hr_view.html', form=overtime_hr_form, overtime_data=overtime_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/overtime_report', methods=["GET"])
@login_required
def overtime_report():
    if not check_access('overtime_report'):
        return redirect(url_for('access_denied'))
    overtime_report = []
    if (request.args.get('from') and request.args.get('to')):
        overtime_report = Employees.query.join(Employees.overtimes, aliased=True) \
            .filter_by(hr=1) \
            .filter(Overtime_form.start_datetime >= to_gregorian(request.args.get('from'))) \
            .filter(Overtime_form.start_datetime < to_gregorian(request.args.get('to'))).all()

    return render_template('overtime_report.html', overtime_report=overtime_report,
        title=translation_obj.forms[session['language']], language=session['language'],
        Overtime_form=Overtime_form, request=request)

@app.route('/loan_request', methods=["GET", "POST"])
@login_required
def loan_request():
    if not check_access('loan_request'):
        return redirect(url_for('access_denied'))
    loan_form = LoanRequestForm(session['language'])
    if request.method == "GET":
        emp_loan_list = Loan_form.query \
            .filter_by(emp_id=current_user.emp_id) \
            .order_by(Loan_form.requested_at.desc()).all()
    if request.method == 'POST':
        if loan_form.validate_on_submit():
            start_date = loan_form.start_date.data
            if isinstance(start_date, str):
                start_date = jdatetime.datetime.strptime(start_date, '%Y-%m-%d')
            month = start_date.month + int(request.form['months'])
            year = start_date.year + int(month/12)
            day = start_date.day
            loan_form.end_date.data = jdatetime.datetime.strftime(jdatetime.date(year, (month % 12), day), '%Y-%m-%d')
            # loan_form.end_date = loan_form.start_date
            loan = add_loan_request(loan_form, current_user.emp_id)
            if loan == "success":
                flash(message_obj.loan_request_sent[session['language']], 'success')
            else:
                flash(message_obj.loan_request_not_sent[session['language']], 'error')
        else:
            flash(loan_form.errors)
        return redirect(url_for('loan_request'))
    return render_template('loan_request.html', form=loan_form, emp_loan_list=emp_loan_list,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/emp_autocomplete', methods=['GET'])
@login_required
def emp_autocomplete():
    search = request.args.get('q')
    name = Employees.name
    lname = Employees.lname
    if session['language'] == 'en':
        name = Employees.name_english
        lname = Employees.lname_english
    employees = db.session.query(Employees.id, name, lname) \
        .filter(Employees.id != current_user.emp_id) \
        .filter((Employees.id.like('%' + str(search) + '%') | Employees.name.like('%' + str(search) + '%') | Employees.lname.like('%' + str(search) + '%') | Employees.name_english.like('%' + str(search) + '%') | Employees.lname_english.like('%' + str(search) + '%')))
    result = [({'value': mv[0], 'label': mv[0] + ' ' + mv[1] + ' ' + mv[2]}) for mv in employees.limit(10).all()]
    message = ''
    if not result :
        message = translation_obj.not_found[session['language']]
    return jsonify(result = result, message = message)

@app.route('/last_date_of_month', methods=['POST'])
@login_required
def last_date_of_month():
    date = jdatetime.datetime.strptime(request.form['date'], '%Y-%m-%d')
    last_day = get_last_date_of_month(date)
    miladi_date = last_day.togregorian()
    if not miladi_date:
        message = translation_obj.not_found[session['language']]
    return jsonify(year=miladi_date.year, month=miladi_date.month, day=miladi_date.day)

@app.route('/user_autocomplete', methods=['GET'])
@login_required
def user_autocomplete():
    search = request.args.get('q')
    name = Employees.name
    lname = Employees.lname
    if session['language'] == 'en':
        name = Employees.name_english
        lname = Employees.lname_english
    if request.args.get('all'):
        employees = db.session.query(Employees.id, name, lname) \
            .filter((Employees.id.like('%' + str(search) + '%') | Employees.name.like('%' + str(search) + '%') | Employees.lname.like('%' + str(search) + '%') | Employees.name_english.like('%' + str(search) + '%') | Employees.lname_english.like('%' + str(search) + '%')))
    else:
        employees = db.session.query(Employees.id, name, lname) \
            .filter(~Employees.users.any()) \
            .filter(Employees.position_history.any(status=1)) \
            .filter((Employees.id.like('%' + str(search) + '%') | Employees.name.like('%' + str(search) + '%') | Employees.lname.like('%' + str(search) + '%') | Employees.name_english.like('%' + str(search) + '%') | Employees.lname_english.like('%' + str(search) + '%')))

    result = [({'value': mv[0], 'label': mv[0] + ' ' + mv[1] + ' ' + mv[2]}) for mv in employees.limit(10).all()]
    message = ''
    if not result :
        message = translation_obj.not_found[session['language']]
    return jsonify(result = result, message = message)

@app.route('/equipment_autocomplete', methods=['GET'])
@login_required
def equipment_autocomplete():
    search = request.args.get('q')
    name = Equipment.name
    if session['language'] == 'en':
        name = Equipment.name_english
    employees = db.session.query(Equipment.id, name, Equipment.model, Equipment.serial) \
        .filter_by(in_use=0) \
        .filter((Equipment.name.like('%' + str(search) + '%') | Equipment.name_english.like('%' + str(search) + '%') | Equipment.serial.like('%' + str(search) + '%')))
    result = [({'value': mv[0], 'label': mv[1] + '-' + mv[2] + '  (' + mv[3] + ')' }) for mv in employees.limit(10).all()]
    message = ''
    if not result :
        message = translation_obj.not_found[session['language']]
    return jsonify(result = result, message = message)

@app.route('/loan_guarantor', methods=["GET"])
@login_required
def loan_guarantor():
    if not check_access('loan_guarantor'):
        return redirect(url_for('access_denied'))
    emp_loan_guarantor = Loan_form.query \
        .filter_by(guarantor_id=current_user.emp_id, guarantor=None) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_guarantor.html', emp_loan_guarantor=emp_loan_guarantor,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_guarantor/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_guarantor_view(loan_id):
    if not check_access('loan_guarantor'):
        return redirect(url_for('access_denied'))
    loan_guarantor_form = LoanGuarantorForm(session['language'])
    if request.method == "GET":
        loan_data = Loan_form.query \
            .filter_by(id=loan_id).first()
    if request.method == 'POST':
        if loan_guarantor_form.validate_on_submit():
            try:
                loan_form = Loan_form.query.get(loan_id)
                loan_form.guarantor = bool(int(request.form['guarantor']))
                loan_form.finalized_at=datetime.datetime.now()
                db.session.commit()
                if request.form['guarantor'] == '0':
                    flash(message_obj.loan_request_guarantor_rejected[session['language']], 'success')
                else:
                    flash(message_obj.loan_request_guarantor_accepted[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.loan_request_guarantor_accepted[session['language']], 'error')
        else:
            flash(loan_guarantor_form.errors)
        return redirect(url_for('loan_guarantor'))
    return render_template('loan_guarantor_view.html', form=loan_guarantor_form, loan_data=loan_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_hr', methods=["GET"])
@login_required
def loan_hr():
    if not check_access('loan_hr'):
        return redirect(url_for('access_denied'))
    emp_loan_hr = Loan_form.query \
        .filter_by(guarantor=1,hr=None) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_hr.html', emp_loan_hr=emp_loan_hr,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_hr/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_hr_view(loan_id):
    if not check_access('loan_hr'):
        return redirect(url_for('access_denied'))
    loan_hr_form = LoanHRForm(session['language'])
    if request.method == "GET":
        loan_data = Loan_form.query \
            .filter_by(id=loan_id).first()
    if request.method == 'POST':
        if loan_hr_form.validate_on_submit():
            try:
                loan_form = Loan_form.query.get(loan_id)
                loan_form.hr = bool(int(request.form['hr']))
                loan_form.hr_id = current_user.emp_id
                loan_form.finalized_at=datetime.datetime.now()
                db.session.commit()
                if request.form['hr'] == '0':
                    flash(message_obj.loan_request_rejected[session['language']], 'success')
                else:
                    flash(message_obj.loan_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.loan_request_accepted[session['language']], 'error')
        else:
            flash(loan_hr_form.errors)
        return redirect(url_for('loan_hr'))
    return render_template('loan_hr_view.html', form=loan_hr_form, loan_data=loan_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_presidency', methods=["GET"])
@login_required
def loan_presidency():
    if not check_access('loan_presidency'):
        return redirect(url_for('access_denied'))
    emp_loan_presidency = Loan_form.query \
        .filter_by(guarantor=1,hr=1) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_presidency.html', emp_loan_presidency=emp_loan_presidency,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_presidency/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_presidency_view(loan_id):
    if not check_access('loan_presidency'):
        return redirect(url_for('access_denied'))
    loan_presidency_form = LoanPresidencyForm(session['language'])
    if request.method == "GET":
        loan_data = Loan_form.query \
            .filter_by(id=loan_id).first()
    if request.method == 'POST':
        if loan_presidency_form.validate_on_submit():
            try:
                loan_form = Loan_form.query.get(loan_id)
                loan_form.presidency = bool(int(request.form['presidency']))
                loan_form.presidency_id = current_user.emp_id
                loan_form.finalized_at=datetime.datetime.now()
                db.session.commit()
                if request.form['presidency'] == '0':
                    flash(message_obj.loan_request_rejected[session['language']], 'success')
                else:
                    flash(message_obj.loan_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.loan_request_accepted[session['language']], 'error')
        else:
            flash(loan_presidency_form.errors)
        return redirect(url_for('loan_presidency'))
    return render_template('loan_presidency_view.html', form=loan_presidency_form, loan_data=loan_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_finance', methods=["GET"])
@login_required
def loan_finance():
    if not check_access('loan_finance'):
        return redirect(url_for('access_denied'))
    emp_loan_finance = Loan_form.query \
        .filter_by(guarantor=1,hr=1,presidency=1) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_finance.html', emp_loan_finance=emp_loan_finance,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_finance/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_finance_view(loan_id):
    if not check_access('loan_finance'):
        return redirect(url_for('access_denied'))
    loan_finance_form = LoanFinanceForm(session['language'])
    if request.method == "GET":
        loan_data = Loan_form.query \
            .filter_by(id=loan_id).first()
    if request.method == 'POST':
        if loan_finance_form.validate_on_submit():
            try:
                loan_form = Loan_form.query.get(loan_id)
                loan_form.finance = bool(int(request.form['finance']))
                loan_form.finance_id = current_user.emp_id
                loan_form.finalized_at=datetime.datetime.now()
                db.session.commit()
                if request.form['finance'] == '0':
                    flash(message_obj.loan_request_rejected[session['language']], 'success')
                else:
                    flash(message_obj.loan_request_accepted[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.loan_request_accepted[session['language']], 'error')
        else:
            flash(loan_finance_form.errors)
        return redirect(url_for('loan_finance'))
    return render_template('loan_finance_view.html', form=loan_finance_form, loan_data=loan_data,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/resign_request', methods=["GET", "POST"])
@login_required
def resign_request():
    if not check_access('resign_request'):
        return redirect(url_for('access_denied'))
    resign_form = ResignRequestForm(session['language'])
    if request.method == "POST":
        resign = send_resign_request(resign_form, current_user.emp_id)
        if resign == "success":
            flash(message_obj.resign_request_sent[session['language']], 'success')
        else:
            flash(message_obj.resign_request_not_sent[session['language']], 'error')
        return redirect(request.referrer)
    return render_template('resign_request.html',
        title=translation_obj.forms[session['language']], form=resign_form,
        language=session['language'])

@app.route('/add_equipment', methods=["GET", "POST"])
@login_required
def add_equipment():
    if not check_access('add_equipment'):
        return redirect(url_for('access_denied'))
    emp_id = request.args.get("emp_id")
    form = AddEquipmentForm()
    all_equipment = ""
    if request.method == "GET":
        all_equipment = Equipment.query.all()
    if request.method == "POST":
        result = assign_equipment(request, emp_id)
        if result == "success":
            flash(message_obj.equipment_added[session['language']], 'success')
        else:
            flash(message_obj.equipment_not_added[session['language']], 'error')
        return redirect(request.referrer)
    return render_template('add_equipment.html', emp_id=emp_id,
        title=translation_obj.forms[session['language']], form=form, all_equipment=all_equipment,
        language=session['language'])

@app.route('/emp_resign_request', methods=["GET", "POST"])
@login_required
def emp_resign_request():
    if not check_access('emp_resign_request'):
        return redirect(url_for('access_denied'))
    if request.method == "GET":
         list_of_resigns = db.session.query(Resign_form, Employees).join(Resign_form,
        (Resign_form.emp_id == Employees.id)).all()

    return render_template('emp_resign_request.html', list_of_resigns=list_of_resigns,
                           title=translation_obj.employee_forms[session['language']], language=session['language'],
                        )

@app.route("/department_setting", methods=['GET', 'POST'])
@login_required
def department_setting():
    if not check_access('department_setting'):
        return redirect(url_for('access_denied'))
    department_form = departmentForm(session['language'])
    departments = Departments.query.all()
    if request.method == 'POST':
        department = send_department(department_form)
        if department == "success":
            flash(message_obj.add_department[session['language']], 'success')
        else:
            flash(message_obj.add_department_not[session['language']], 'error')
        return redirect(request.referrer)
    return render_template('department_setting.html', form=department_form, departments=departments,
        title=translation_obj.forms[session['language']], language=session['language'])


@app.route("/holiday", methods=['GET', 'POST'])
@login_required
def holiday():
    if not check_access('holiday'):
        return redirect(url_for('access_denied'))
    holiday_form = HolidayForm(session['language'])
    if request.method == "GET":
        # Get the year from url or set current year as default
        year = jdatetime.date.today().year
        if request.args.get('year'):
            year = request.args.get('year')
        start_end_year = Holiday.query.with_entities(func.max(Holiday.date).label('maxdate'), func.min(Holiday.date).label('mindate')).first()
        
        start = jdatetime.date(year=int(year),month=1,day=1)
        last_day = 30 if start.isleap() else 29
        end = jdatetime.date(year=int(year),month=12,day=last_day)
        holidays = Holiday.query \
            .filter(Holiday.date >= to_gregorian(start.strftime('%Y-%m-%d'))) \
            .filter(Holiday.date < to_gregorian(end.strftime('%Y-%m-%d'))) \
            .order_by(Holiday.date.asc()).all()
        holiday_prepar = {}
        for holiday in holidays:
            if not to_jalali(holiday.date, type='date').month in holiday_prepar:
                holiday_prepar[to_jalali(holiday.date, type='date').month] = []
            holiday_prepar[to_jalali(holiday.date, type='date').month].append(holiday)
            
    if request.method == 'POST':
        if holiday_form.validate_on_submit():
            holiday = add_holiday(holiday_form)
            if holiday == "success":
                flash(message_obj.holiday_added[session['language']], 'success')
            else:
                flash(message_obj.holiday_not_added[session['language']], 'error')
        else:
            flash(holiday_form.errors)
        return redirect(url_for('holiday'))
    return render_template('holiday.html', form=holiday_form, start_end_year=start_end_year, holidays=holiday_prepar,
        title=translation_obj.forms[session['language']], language=session['language'], year_url=year)

@app.route("/delete_holiday/<int:holiday_id>", methods=['GET'])
@login_required
def delete_holiday(holiday_id):
    if not check_access('delete_holiday'):
        return redirect(url_for('access_denied'))
    try:
        holiday = Holiday.query.get(holiday_id)
        db.session.delete(holiday)
        db.session.commit()
        flash(message_obj.holiday_deleted[session['language']], 'success')
    except IOError as exc:
        flash(message_obj.holiday_not_deleted[session['language']], 'error')
    return redirect(url_for('holiday'))

@app.route("/update_holiday", methods=['GET', 'POST'])
@login_required
def update_holiday():
    if not check_access('update_holiday'):
        return redirect(url_for('access_denied'))
    holiday_form = HolidayForm(session['language'])
    if request.method == "GET":
        holiday = Holiday.query.get(request.args.get('id'))
        data = {'id': holiday.id, 'date': to_jalali(holiday.date), 'title': holiday.title, 'title_english': holiday.title_english}
        return jsonify(data)
    elif request.method == "POST":
        if holiday_form.validate_on_submit():
            try:
                holiday = Holiday.query.get(request.form['id'])
                holiday.date = to_gregorian(request.form['date'])
                holiday.title = request.form['title']
                holiday.title_english = request.form['title_english']
                db.session.commit()
                flash(message_obj.holiday_updated[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.holiday_not_updated[session['language']], 'error')
        else:
            flash(holiday_form.errors)
    return redirect(url_for('holiday'))

@app.route("/attendance_file", methods=['GET', 'POST'])
@login_required
def attendance_file():
    if not check_access('attendance_file'):
        return redirect(url_for('access_denied'))
    attendance_form = AttendanceForm(session['language'])
    if request.method == "GET":
        attendance_file_list = AttendanceFile.query.all()
    if request.method == 'POST':
        if attendance_form.validate_on_submit():
            overtime = add_attendance(attendance_form)
            if overtime == "success":
                flash(message_obj.attendance_file_saved[session['language']], 'success')
            else:
                flash(message_obj.attendance_file_not_saved[session['language']], 'error')
        else:
            flash(attendance_form.errors)
        return redirect(url_for('attendance_file'))
    return render_template('attendance_file.html', form=attendance_form, attendance_file_list=attendance_file_list,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route("/delete_attendance_file/<int:attendance_id>", methods=['GET'])
@login_required
def delete_attendance_file(attendance_id):
    if not check_access('delete_attendance_file'):
        return redirect(url_for('access_denied'))
    try:
        attendance = AttendanceFile.query.get(attendance_id)
        if attendance.raw_file_url and os.path.exists(os.path.join(f"./rpc_package" + attendance.raw_file_url)):
            os.remove(os.path.join(f"./rpc_package" + attendance.raw_file_url))
        if attendance.file_url and os.path.exists(os.path.join(f"./rpc_package" + attendance.file_url)):
            os.remove(os.path.join(f"./rpc_package" + attendance.file_url))
        db.session.delete(attendance)
        db.session.commit()
        flash(message_obj.attendance_file_deleted[session['language']], 'success')
    except IOError as exc:
        flash(message_obj.attendance_file_not_deleted[session['language']], 'error')
    return redirect(url_for('attendance_file'))

@app.route("/process_attendance_file/<int:attendance_id>", methods=['GET'])
@login_required
def process_attendance_file(attendance_id):
    if not check_access('process_attendance_file'):
        return redirect(url_for('access_denied'))
    try:
        attendance = AttendanceFile.query.get(attendance_id)
        start = jdatetime.date(year=attendance.year, month=attendance.month, day=1)
        end = get_last_date_of_month(start)
        holidays = Holiday.query.filter(Holiday.date >= to_gregorian(start)) \
            .filter(Holiday.date <= to_gregorian(end)).all()
        hourly_leaves = Leave_form.query.filter_by(hr=1, supervisor=1, leave_type=1) \
            .filter(Leave_form.start_datetime >= to_gregorian(start)) \
            .filter(Leave_form.end_datetime <= to_gregorian(end)).all()
        daily_leaves = Leave_form.query.filter_by(hr=1, supervisor=1, leave_type=0) \
            .filter(Leave_form.start_datetime >= to_gregorian(start)) \
            .filter(Leave_form.end_datetime <= to_gregorian(end)).all()
        att_obj = Attendance('sonbola', 1400, path_att=attendance.raw_file_url, holidays=holidays, hourly_leaves=hourly_leaves, daily_leaves=daily_leaves)
        att_obj.read_excel()
        att_obj.drop_cols()
        
        flash(message_obj.attendance_file_processed[session['language']], 'success')
    except IOError as exc:
        flash(message_obj.attendance_file_not_processed[session['language']], 'error')
    return redirect(url_for('attendance_file'))

@app.route("/position_setting", methods=['GET', 'POST'])
@login_required
def position_setting():
    return render_template('position_setting.html', language=session['language'])

@app.route("/my_equipment", methods=['GET'])
@login_required
def my_equipment():
    if not check_access('my_equipment'):
        return redirect(url_for('access_denied'))
    form = AcceptEquipmentForm()
    if request.method == "GET":
        my_equipment = Employee_equipment.query \
            .filter_by(emp_id=current_user.emp_id) \
            .order_by(Employee_equipment.id.desc()).all()
    return render_template('my_equipment.html', form=form, my_equipment=my_equipment, language=session['language'])

@app.route("/recieved_equipment/<int:equipment_id>", methods=['GET'])
@login_required
def recieved_equipment(equipment_id):
    if not check_access('recieved_equipment'):
        return redirect(url_for('access_denied'))
    if request.method == "GET":
        try:
            emp_equipment = Employee_equipment.query.get(equipment_id)
            if emp_equipment.emp_id == current_user.emp_id:
                emp_equipment.status = False
                db.session.commit()
            flash(message_obj.equipment_confirm[session['language']], 'success')
        except IOError as exc:
            flash(message_obj.equipment_not_confirm[session['language']], 'error')
    return redirect(url_for('my_equipment'))

@app.route("/equipment", methods=['GET', 'POST'])
@login_required
def equipment():
    if not check_access('equipment'):
        return redirect(url_for('access_denied'))
    equipment_form = EquipmentForm(session['language'])
    if request.method == "GET":
        status = request.args.get('status')
        page = request.args.get('page') if request.args.get('page') else 1
        equipments = Equipment.query.order_by(Equipment.id.desc())
        if status == '0' or status == '1' :
            equipments = equipments.filter(Equipment.in_use==status)
        equipments = equipments.paginate(per_page=15,page=int(page),error_out=True)

    if request.method == 'POST':
        if equipment_form.validate_on_submit():
            if add_new_equipment(equipment_form) == "success":
                flash(message_obj.equipment_added[session['language']], 'success')
            else:
                flash(message_obj.equipment_not_added[session['language']], 'error')
        else:
            flash(equipment_form.errors)
        return redirect(url_for('equipment'))
    return render_template('equipment.html', form=equipment_form, equipments=equipments, Employee_equipment=Employee_equipment,
        title=translation_obj.forms[session['language']], language=session['language'], request=request)

@app.route("/delete_equipment/<int:equipment_id>", methods=['GET'])
@login_required
def delete_equipment(equipment_id):
    if not check_access('delete_equipment'):
        return redirect(url_for('access_denied'))
    try:
        equipment = Equipment.query.get(equipment_id)
        db.session.delete(equipment)
        db.session.commit()
        flash(message_obj.equipment_deleted[session['language']], 'success')
    except IOError as exc:
        flash(message_obj.equipment_not_deleted[session['language']], 'error')
    return redirect(url_for('equipment'))

@app.route("/update_equipment", methods=['GET', 'POST'])
@login_required
def update_equipment():
    if not check_access('update_equipment'):
        return redirect(url_for('access_denied'))
    equipment_form = EquipmentForm(session['language'])
    if request.method == "GET":
        equipment = Equipment.query.get(request.args.get('id'))
        data = {
            'id': equipment.id,
            'name': equipment.name,
            'name_english': equipment.name_english,
            'serial': equipment.serial,
            'model': equipment.model,
            'category': equipment.category
        }
        return jsonify(data)
    elif request.method == "POST":
        if equipment_form.validate_on_submit():
            try:
                equipment = Equipment.query.get(request.form['id'])
                equipment.name = request.form['name']
                equipment.name_english = request.form['name_english']
                equipment.serial = request.form['serial']
                equipment.model = request.form['model']
                equipment.category = request.form['category']
                db.session.commit()
                flash(message_obj.equipment_updated[session['language']], 'success')
            except IOError as exc:
                flash(message_obj.equipment_not_updated[session['language']], 'error')
        else:
            flash(equipment_form.errors)
    return redirect(url_for('equipment'))

@app.route("/emp_equipment", methods=['GET', 'POST'])
@login_required
def emp_equipment():
    if not check_access('emp_equipment'):
        return redirect(url_for('access_denied'))
    assign_equipment_form = AssignEquipmentForm(session['language'])
    surrender_equipment_form = SurrenderEquipmentForm(session['language'])
    if request.method == "GET":
        status = request.args.get('status')
        employee_id = request.args.get('employee_id')
        page = request.args.get('page') if request.args.get('page') else 1
        emp_equipments = Employee_equipment.query \
            .order_by(Employee_equipment.id.desc())
        if status == '0' or status == '1' or status == 'None':
            if status == 'None':
                status = None
            emp_equipments = emp_equipments.filter(Employee_equipment.status==status)
        if employee_id != '' and employee_id != None:
            emp_equipments = emp_equipments.filter(Employee_equipment.emp_id==employee_id)
        emp_equipments = emp_equipments.paginate(per_page=15,page=int(page),error_out=True)

    if request.method == 'POST':
        if assign_equipment_form.validate_on_submit():
            if add_employee_equipment(assign_equipment_form) == "success":
                flash(message_obj.equipment_assigned[session['language']], 'success')
            else:
                flash(message_obj.equipment_not_assigned[session['language']], 'error')
        else:
            flash(assign_equipment_form.errors)
        return redirect(url_for('emp_equipment'))
    return render_template('emp_equipment.html', form=assign_equipment_form, emp_equipments=emp_equipments,
        title=translation_obj.forms[session['language']], surrender_form=surrender_equipment_form, language=session['language'])

@app.route("/surrender_equipment", methods=['POST'])
@login_required
def surrender_equipment():
    if not check_access('surrender_equipment'):
        return redirect(url_for('access_denied'))
    if request.method == 'POST':
        surrender_equipment_form = SurrenderEquipmentForm(session['language'])
        if surrender_equipment_form.validate_on_submit():
            if surrender_equipment_update(surrender_equipment_form) == "success":
                flash(message_obj.equipment_surrender[session['language']], 'success')
            else:
                flash(message_obj.equipment_not_surrender[session['language']], 'error')
        else:
            flash(surrender_equipment_form.errors)
        return redirect(url_for('emp_equipment'))

@app.route("/download_equipment_file/<int:equipment_id>", methods=['GET'])
@login_required
def download_equipment_file(equipment_id):
    if not check_access('download_equipment_file'):
        return redirect(url_for('access_denied'))
    if request.method == "GET":
        try:
            emp_equipment = Employee_equipment.query.get(equipment_id)
            path = os.path.join('.' + emp_equipment.file_url)
        except IOError as exc:
            flash(message_obj.file_not_downloaded[session['language']], 'error')
    return send_file(path, as_attachment=True)

@app.route("/view_resign_request", methods=['GET', 'POST'])
@login_required
def view_resign_request():
    if not check_access('view_resign_request'):
        return redirect(url_for('access_denied'))
    form = AcceptEquipmentForm()
    resign_id = request.args.get('resign')
    resign = db.session.query(Resign_form, Employees).join(Resign_form, Resign_form.id == resign_id).first()
    equipment = db.session.query(Employee_equipment, Equipment).join(Employee_equipment,
        (Equipment.id == Employee_equipment.equipment_id)).filter(Employee_equipment.emp_id==resign[0].emp_id, Employee_equipment.delivered == None).all()
    return render_template('view_resign_request.html', form=form, equipment=equipment, resign=resign, language=session['language'])

@app.route("/deliver_equipment", methods=['POST'])
@login_required
def deliver_equipment():
    if not check_access('deliver_equipment'):
        return redirect(url_for('access_denied'))
    result = accept_equipment(request, "admin")
    if result == "success":
        flash(message_obj.delivered[session['language']], 'success')
    else:
        flash(message_obj.not_delivered[session['language']], 'error')
    return redirect(request.referrer)

@app.route("/read_notification/<int:notification_id>", methods=['GET'])
@login_required
def read_notification(notification_id):
    # if not check_access('read_notification'):
    #     return redirect(url_for('access_denied'))
    notification = Notification.query.filter_by(id=notification_id).first()
    if notification.emp_id == current_user.emp_id:
        notification.read = True
        db.session.commit()
        return redirect(notification.url)
    return redirect(request.referrer)

@app.route("/accept_reject_resign_request", methods=['GET'])
@login_required
def accept_reject_resign_request():
    if not check_access('accept_reject_resign_request'):
        return redirect(url_for('access_denied'))
    resin = accept_reject_resign(request)
    if resin == "success":
        flash(message_obj.action_performed[session['language']], 'success')
    else:
        flash(message_obj.action_not_performed[session['language']], 'error')
    return redirect(request.referrer)

@app.route("/access_denied", methods=['GET', 'POST'])
@login_required
def access_denied():
    return render_template('page_layout/access_denied.html', language=session['language'])
