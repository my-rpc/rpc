from flask import render_template, url_for, redirect, request, jsonify, flash
from flask_login import login_user, current_user, logout_user, login_required
from rpc_package import app, pass_crypt, db
from werkzeug.utils import secure_filename
from rpc_package.forms import CreateUserForm, LoginForm, EmployeeForm, UploadCVForm, UploadGuarantorForm, UploadEducationalDocsForm, \
        UploadTinForm, UploadTazkiraForm, UploadExtraDocsForm
from rpc_package.form_dynamic_language import *
from rpc_package.rpc_tables import Users, Employees, Documents, User_roles, Permanent_addresses, Current_addresses, Districts, \
    Emails, Phone, Provinces
from rpc_package.utils import EmployeeValidator, message_to_client_403, message_to_client_200, get_uploaded_file
import os
from datetime import datetime



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
    guarantor = UploadGuarantorForm()
    education = UploadEducationalDocsForm()
    tin = UploadTinForm()
    tazkira = UploadTazkiraForm()
    extra_docs = UploadExtraDocsForm()
    emp_id = 0
    emp_id = request.args.get("emp_id")

    if request.method == "GET":
        cv_doc = Documents.query.filter_by(emp_id=emp_id, name="cv").first()
        guarantor_doc = Documents.query.filter_by(emp_id=emp_id, name="guarantor").first()
        tazkira_doc = Documents.query.filter_by(emp_id=emp_id, name="tazkira").first()
        education_doc = Documents.query.filter_by(emp_id=emp_id, name="education").first()
        tin_doc = Documents.query.filter_by(emp_id=emp_id, name="tin").first()
        extra_doc = Documents.query.filter_by(emp_id=emp_id, name="extra").first()

    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        if guarantor.flag.data == "guarantor": 
            guarantor = request.files['guarantor']
            guarantor.filename = "Guarantor-"+emp_id+".pdf"
            path = os.path.join(workingdir+"/rpc_package/static/files/guarantor", guarantor.filename)
            doc = Documents.query.filter_by(emp_id=emp_id, name="guarantor").first()
            document = Documents(
                            emp_id=emp_id,
                            name="guarantor",
                            url="/static/files/guarantor/"+guarantor.filename)
            db.session.add(document)
            db.session.commit()
            guarantor.save(path)
            return redirect(request.referrer)
        if  cv_form.flag.data == "cv":
            path = get_uploaded_file(emp_id, request, "cv")
            document = Documents(
                            emp_id=emp_id,
                            name="cv",
                            url="/static/files/cv/"+request.files['cv'].filename)
            db.session.add(document)
            db.session.commit()
            request.files['cv'].save(path)
            return redirect(request.referrer)
        if education and education.flag.data == "education":
            education = request.files['education']
            education.filename = "Education-"+emp_id+".pdf"
            path = os.path.join(workingdir+"/rpc_package/static/files/education", education.filename)
            doc = Documents.query.filter_by(emp_id=emp_id, name="education").first()
            document = Documents(
                            emp_id=emp_id,
                            name="education",
                            url="/static/files/education/"+education.filename)
            db.session.add(document)
            db.session.commit()
            education.save(path)
            # flash("uploaded")
            return redirect(request.referrer)
        if tin and tin.flag.data == "tin":
            try:
                tin = request.files['tin']
                tin.filename = "TIN-"+emp_id+".pdf"
                path = os.path.join(workingdir+"/rpc_package/static/files/tin", tin.filename)
                doc = Documents.query.filter_by(emp_id=emp_id, name="tin").first()
                document = Documents(
                                emp_id=emp_id,
                                name="tin",
                                url="/static/files/tin/"+tin.filename)
                db.session.add(document)
                db.session.commit()
                tin.save(path)
                flash(f"TIN uploaded", "success")
            except:
                flash(f"TIN not uploaded", "error")


            return redirect(request.referrer)
        if tazkira and tazkira.flag.data == "tazkira":
            tazkira = request.files['tazkira']
            tazkira.filename = "Tazkira-"+emp_id+".pdf"
            path = os.path.join(workingdir+"/rpc_package/static/files/tazkira", tazkira.filename)
            doc = Documents.query.filter_by(emp_id=emp_id, name="tazkira").first()
            document = Documents(
                            emp_id=emp_id,
                            name="tazkira",
                            url="/static/files/tazkira/"+tazkira.filename)
            db.session.add(document)
            db.session.commit()
            tazkira.save(path)
            flash("uploaded")

            return redirect(request.referrer)
        if extra_docs and extra_docs.flag.data == "extra_docs":
            extra_docs = request.files['extra_docs']
            extra_docs.filename = "Extra-"+emp_id+".pdf"
            path = os.path.join(workingdir+"/rpc_package/static/files/extra_docs", extra_docs.filename)
            doc = Documents.query.filter_by(emp_id=emp_id, name="extra").first()
            document = Documents(
                            emp_id=emp_id,
                            name="extra",
                            url="/static/files/extra_docs/"+extra_docs.filename)
            db.session.add(document)
            db.session.commit()
            extra_docs.save(path)
            flash("uploaded")
            return redirect(request.referrer)
    # return message_to_client_200(
    #             message_obj.create_new_employee_update[language].format(request.form['employee_id']))
    return render_template("add_documents.html", title='Add Employee Documents',
                           language=language,
                           translation=translation_obj, emp_id=emp_id, extra_docs_form=extra_docs,
                            tazkira_form=tazkira, form=cv_form, tin_form=tin, education_form=education,
                             guarantor_form=guarantor, message_obj=message_obj,
                             cv_doc=cv_doc, guarantor_doc=guarantor_doc, tin_doc=tin_doc,
                             education_doc=education_doc, extra_doc=extra_doc, tazkira_doc=tazkira_doc
                             )

# @app.route("/delete_document", methods=['GET'])
# @login_required
# def load_districts():

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
    if request.method == 'POST':
        if EmployeeValidator.emp_id_validator(request.form['employee_id']):
            sel_emp = Employees.query.filter_by(id = update_employee_form.employee_id.data).first()
            phones = Phone.query.filter_by(emp_id = update_employee_form.employee_id.data).all()
            emails = Emails.query.filter_by(emp_id = update_employee_form.employee_id.data).all()
            

            try:
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
                sel_emp.birthday = update_employee_form.birthday.data
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
                    cur_add = Current_addresses.query.filter_by(emp_id = update_employee_form.employee_id.data).first()

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
                    per_add = Permanent_addresses.query.filter_by(emp_id = update_employee_form.employee_id.data).first()
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
            except IOError as exc:
                print(exc)
                return message_to_client_403(message_obj.create_new_employee_update_not[language])
            return message_to_client_200(
                message_obj.create_new_employee_update[language].format(request.form['employee_id']))
        else:
            return message_to_client_403(message_obj.create_new_employee_update_not[language])
            

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
        update_employee_form.last_name_english.data = emp.lname_english
        update_employee_form.father_name_english.data = emp.fname_english
        update_employee_form.grand_name_english.data = emp.gname_english
        update_employee_form.tin.data = emp.tin
        update_employee_form.tazkira.data = emp.tazkira
        update_employee_form.birthday.data = emp.birthday
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
                            +"<p class='px-3'>" \
                            + str(cur_address) + ", " + str(cur_district_name) + ", " + str(cur_province_name) +"</p> <br> " \
                            + "<h5 class=' text-primary'> Current address: </h5> <p class='px-3'>" + str(cur_address_eng) + ", " \
                            + str(cur_district_name_eng) + ", " + str(cur_province_name_eng) \
                            + "</p> <span onClick=\"showAddress(\'cur-address\')\"> <i class='fad fa-edit text-info'></i> </span> </div>"

        permanent_addresses = "<div class='py-4 d-flex'> <h5 class=' text-primary'> ادرس اصلی: </h5>" \
                              + "<p class='px-3 '>" \
                              + str(per_address) + ", " + str(per_district_name) + ", " + str(per_province_name)+ "</p> <br>" \
                              + "<h5 class=' text-primary'> Permanent address: </h5> <p class='px-3 '>" \
                              + str(per_address_eng) + ", " + str(per_district_name_eng) + ", " + str(per_province_name_eng) \
                              +"</p> <span onClick=\"showAddress(\'per-address\')\"> <i class='fad fa-edit text-info'></i> </span> </div>"

        data = jsonify(render_template('ajax_template/update_employee_form.html', language=language, 
                            form=update_employee_form, translation=translation_obj, message_obj=message_obj), 
                            {'current_add': current_addresses, 'permanent_add': permanent_addresses})
        return data
    else:
        message_to_client_403(message_obj.invalid_message[language])
