from flask import render_template, url_for, redirect, request, jsonify, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from rpc_package import app, pass_crypt, db
from werkzeug.utils import secure_filename
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm, UploadCVForm, UploadGuarantorForm, \
    AddEquipmentForm, ResignRequestForm, UploadEducationalDocsForm, \
    UploadTinForm, UploadTazkiraForm, UploadExtraDocsForm, leaveRequestForm, departmentForm, OvertimeRequestForm, \
    ContractForm, LoanRequestForm, LoanGuarantorForm, LoanHRForm, LoanPresidencyForm, LoanFinanceForm, AcceptEquipmentForm, \
    OvertimeSupervisorForm, OvertimeHRForm, LeaveSupervisorForm, LeaveHRForm

from rpc_package.form_dynamic_language import *

from rpc_package.rpc_tables import Users, Employees, Documents, User_roles, Permanent_addresses, Current_addresses, \
    Contracts, Contract_types, Positions, Position_history, Salary, Employee_equipment, \
    Departments, Overtime_form, Districts, Equipment, Resign_form, Emails, Phone, Provinces, Leave_form, \
    Loan_form, Overtime_reason, Leave_reason
from rpc_package.utils import EmployeeValidator, message_to_client_403, message_to_client_200, to_gregorian, to_jalali
from rpc_package.route_utils import upload_docs, get_profile_info, get_documents, upload_profile_pic, \
    add_contract_form, add_overtime_request, set_contact_update_form_data, update_contract, assign_equipment, send_resign_request,\
    update_employee_data, set_emp_update_form_data, add_leave_request, send_resign_request, send_department, \
    add_loan_request, accept_equipment, accept_reject_resign
import os
import datetime
import jdatetime

@app.route("/create_new_user", methods=['GET', 'POST'])
@login_required
def create_new_user():
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
    return render_template('create_new_user.html', title='Create New User', users=users,
                           form=create_new_user_form, language=session['language'],                            )


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
            if user.status:
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
                           form=add_employee_form, language=session['language'],
                        )


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
                        emp_id=emp_id, extra_docs_form=extra_docs,
                           tazkira_form=tazkira, form=cv_form, tin_form=tin, education_form=education,
                           guarantor_form=guarantor,
                           cv_doc=cv_doc, guarantor_doc=guarantor_doc, tin_doc=tin_doc,
                           education_doc=education_doc, extra_doc=extra_doc, tazkira_doc=tazkira_doc)


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
                        )


@app.route('/employee_details', methods=['GET', "POST"])
@login_required
def employee_details():
    emp_id = request.args.get('emp_id')

    if EmployeeValidator.emp_id_validator(emp_id):
        try:
            sel_emp = Employees.query.get(emp_id)
            phones = db.session.query(Phone).filter_by(emp_id=emp_id).all()
            emails = db.session.query(Emails).filter_by(emp_id=emp_id).all()

            current_addresses = db.session.query(Current_addresses, Provinces, Districts) \
                .join(Provinces, (Current_addresses.province_id == Provinces.id)) \
                .join(Districts, (Current_addresses.district_id == Districts.id)) \
                .filter(Current_addresses.emp_id == emp_id).first()

            permanent_addresses = db.session.query(Permanent_addresses, Provinces, Districts) \
                .join(Provinces, (Permanent_addresses.province_id == Provinces.id)) \
                .join(Districts, (Permanent_addresses.district_id == Districts.id)) \
                .filter(Permanent_addresses.emp_id == emp_id).first()
            employee = sel_emp, phones, emails, current_addresses, permanent_addresses

        except IOError as exc:
            return render_template('employee_details.html', title='Employee Details', language=session['language'])

        return render_template('employee_details.html', title='Employee Details', language=session['language'], employee=employee)
    else:
        print('kdsjflksdjflsdkjfsldkfjsdlkfjsldkfjs')
        flash(message_obj.invalid_message[session['language']], "error")
        return render_template('employee_details.html', title='Employee Details', language=session['language'])


@app.route('/uds_employee', methods=['GET', "POST"])
@login_required
def uds_employee():
    language = 'en'
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
    print(current_user.user_role, current_user.department)
    return render_template('profile.html', title='My Profile', language=session['language'], profile=profile,
                           current_address=current_address,
                           permanent_address=permanent_address, doc_cv=doc_cv, email=email, phone=phone,
                           doc_tazkira=doc_tazkira,
                           doc_guarantor=doc_guarantor, doc_tin=doc_tin, doc_education=doc_education,
                           doc_extra=doc_extra,
                        )


@app.route('/contract_settings')
@login_required
def contract_settings():
    position_history = Position_history.query.all()
    return render_template('contract_settings.html', title='Contact Setting',
        language=session['language'], position_history=position_history)


@app.route('/add_contract', methods=["GET", "POST"])
@login_required
def add_contract():
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



@app.route('/delete_contract', methods=['delete'])
@login_required
def delete_contract():
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
    return upload_profile_pic(request)


@app.route('/leave_request', methods=["GET", "POST"])
@login_required
def leave_request():
    leave_form = leaveRequestForm(session['language'])
    if request.method == "GET":
        my_leave_list = Leave_form.query \
            .filter_by(emp_id=current_user.emp_id) \
            .order_by(Leave_form.requested_at.desc()).all()
    if request.method == 'POST':
        if leave_form.validate_on_submit():
            leave = add_leave_request(leave_form, current_user.emp_id)
            if leave == "success":
                flash(message_obj.leave_request_sent[session['language']], 'success')
            else:
                flash(message_obj.leave_request_not_sent[session['language']], 'error')
        else:
            flash(leave_form.errors)
        return redirect(url_for('leave_request'))
    return render_template('leave_request.html', form=leave_form, my_leave_list=my_leave_list,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/leave_supervisor', methods=["GET"])
@login_required
def leave_supervisor():
    page = request.args.get('page') if request.args.get('page') else 1
    leave_supervisor = Leave_form.query \
        .order_by(Leave_form.requested_at.desc()) \
        .paginate(per_page=10,page=int(page),error_out=True)
    return render_template('leave_supervisor.html', leave_supervisor=leave_supervisor,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/leave_supervisor/<int:leave_id>', methods=["GET", "POST"])
@login_required
def leave_supervisor_view(leave_id):
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
                if request.form['supervisor'] == '0':
                    flash(message_obj.leave_request_rejected[session['language']], 'success')
                else:
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
    overtime_form = OvertimeRequestForm(session['language'])
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
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/overtime_supervisor', methods=["GET"])
@login_required
def overtime_supervisor():
    page = request.args.get('page') if request.args.get('page') else 1
    overtime_supervisor = Overtime_form.query \
        .order_by(Overtime_form.requested_at.desc()) \
        .paginate(per_page=10,page=int(page),error_out=True)
    return render_template('overtime_supervisor.html', overtime_supervisor=overtime_supervisor,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/overtime_supervisor/<int:overtime_id>', methods=["GET", "POST"])
@login_required
def overtime_supervisor_view(overtime_id):
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
                if request.form['supervisor'] == '0':
                    flash(message_obj.overtime_request_rejected[session['language']], 'success')
                else:
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

@app.route('/user_autocomplete', methods=['GET'])
def user_autocomplete():
    search = request.args.get('q')
    name = Employees.name
    lname = Employees.lname
    if session['language'] == 'en':
        name = Employees.name_english
        lname = Employees.lname_english
    employees = db.session.query(Employees.id, name, lname) \
        .filter(~Employees.users.any()) \
        .filter(Employees.position_history.any(status=1)) \
        .filter((Employees.id.like('%' + str(search) + '%') | Employees.name.like('%' + str(search) + '%') | Employees.lname.like('%' + str(search) + '%') | Employees.name_english.like('%' + str(search) + '%') | Employees.lname_english.like('%' + str(search) + '%')))
    result = [({'value': mv[0], 'label': mv[0] + ' ' + mv[1] + ' ' + mv[2]}) for mv in employees.limit(10).all()]
    message = ''
    if not result :
        message = translation_obj.not_found[session['language']]
    return jsonify(result = result, message = message)

@app.route('/loan_guarantor', methods=["GET"])
@login_required
def loan_guarantor():
    emp_loan_guarantor = Loan_form.query \
        .filter_by(guarantor_id=current_user.emp_id, guarantor=None) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_guarantor.html', emp_loan_guarantor=emp_loan_guarantor,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_guarantor/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_guarantor_view(loan_id):
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
    emp_loan_hr = Loan_form.query \
        .filter_by(guarantor=1,hr=None) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_hr.html', emp_loan_hr=emp_loan_hr,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_hr/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_hr_view(loan_id):
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
    emp_loan_presidency = Loan_form.query \
        .filter_by(guarantor=1,hr=1) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_presidency.html', emp_loan_presidency=emp_loan_presidency,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_presidency/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_presidency_view(loan_id):
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
    emp_loan_finance = Loan_form.query \
        .filter_by(guarantor=1,hr=1,presidency=1) \
        .order_by(Loan_form.requested_at.desc()).all()
    return render_template('loan_finance.html', emp_loan_finance=emp_loan_finance,
        title=translation_obj.forms[session['language']], language=session['language'])

@app.route('/loan_finance/<int:loan_id>', methods=["GET", "POST"])
@login_required
def loan_finance_view(loan_id):
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
    if request.method == "GET":
         list_of_resigns = db.session.query(Resign_form, Employees).join(Resign_form,
        (Resign_form.emp_id == Employees.id)).all()

    return render_template('emp_resign_request.html', list_of_resigns=list_of_resigns,
                           title=translation_obj.employee_forms[session['language']], language=session['language'],
                        )

@app.route("/department_setting", methods=['GET', 'POST'])
@login_required
def department_setting():
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


@app.route("/contract_setting", methods=['GET', 'POST'])
@login_required
def contract_setting():
    return render_template('contract_setting.html', language=session['language'])


@app.route("/position_setting", methods=['GET', 'POST'])
@login_required
def position_setting():
    return render_template('position_setting.html', language=session['language'])

@app.route("/my_equipment", methods=['GET', 'POST'])
@login_required
def my_equipment():
    form = AcceptEquipmentForm()
    if request.method == "GET":
        my_equipment = db.session.query(Employee_equipment, Equipment).join(Employee_equipment,
            (Equipment.id == Employee_equipment.equipment_id)).filter(Employee_equipment.emp_id==current_user.emp_id, Employee_equipment.received == None).all()
    received_equipment = db.session.query(Employee_equipment, Equipment).join(Employee_equipment,
        (Equipment.id == Employee_equipment.equipment_id)).filter(Employee_equipment.emp_id==current_user.emp_id, Employee_equipment.received == True, Employee_equipment.delivered == None).all()

    if request.method == "POST":
        result = accept_equipment(request, "employee")
        if result == "success":
            flash(message_obj.add_department[session['language']], 'success')
        else:
            flash(message_obj.add_department_not[session['language']], 'error')
        return redirect(request.referrer)
    return render_template('my_equipment.html', form=form, received_equipment=received_equipment, my_equipment=my_equipment, language=session['language'])


@app.route("/view_resign_request", methods=['GET', 'POST'])
@login_required
def view_resign_request():
    form = AcceptEquipmentForm()
    resign_id = request.args.get('resign')
    resign = db.session.query(Resign_form, Employees).join(Resign_form, Resign_form.id == resign_id).first()
    equipment = db.session.query(Employee_equipment, Equipment).join(Employee_equipment,
        (Equipment.id == Employee_equipment.equipment_id)).filter(Employee_equipment.emp_id==resign[0].emp_id, Employee_equipment.delivered == None).all()
    return render_template('view_resign_request.html', form=form, equipment=equipment, resign=resign, language=session['language'])

@app.route("/deliver_equipment", methods=['POST'])
@login_required
def deliver_equipment():
    result = accept_equipment(request, "admin")
    if result == "success":
        flash(message_obj.delivered[session['language']], 'success')
    else:
        flash(message_obj.not_delivered[session['language']], 'error')
    return redirect(request.referrer)

@app.route("/accept_reject_resign_request", methods=['GET'])
@login_required
def accept_reject_resign_request():
    resin = accept_reject_resign(request)
    if resin == "success":
        flash(message_obj.action_performed[session['language']], 'success')
    else:
        flash(message_obj.action_not_performed[session['language']], 'error')
    return redirect(request.referrer)
