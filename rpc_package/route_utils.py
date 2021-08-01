import os

from rpc_package import db
from rpc_package.rpc_tables import Documents, Users, Employees, Emails, User_roles, Current_addresses, Permanent_addresses, Phone, \
        Provinces, Districts
from flask import session


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
                (Users.role == User_roles.id)).join(Employees, (Users.emp_id == Employees.id)).filter(Employees.id == session['emp_id']).first()
    current_address = db.session.query(Current_addresses, Provinces, Districts).join(
        Current_addresses, (Provinces.id == Current_addresses.province_id)).join(Districts, (Current_addresses.district_id == Districts.id)
    ).filter(Current_addresses.emp_id == session['emp_id']).first()
    permanent_address = db.session.query(Permanent_addresses, Provinces, Districts).join(
        Permanent_addresses, (Provinces.id == Permanent_addresses.province_id)).join(Districts, (Permanent_addresses.district_id == Districts.id)
    ).filter(Permanent_addresses.emp_id == session['emp_id']).first()
    doc_cv = Documents.query.filter_by(emp_id=session['emp_id'], name="cv").first()
    doc_tazkira = Documents.query.filter_by(emp_id=session['emp_id'], name="tazkira").first()
    doc_guarantor = Documents.query.filter_by(emp_id=session['emp_id'], name="guarantor").first()
    doc_tin = Documents.query.filter_by(emp_id=session['emp_id'], name="tin").first()
    doc_education = Documents.query.filter_by(emp_id=session['emp_id'], name="education").first()
    doc_extra = Documents.query.filter_by(emp_id=session['emp_id'], name="extra").first()
    email = Emails.query.filter_by(emp_id=session['emp_id']).first()
    phone = Phone.query.filter_by(emp_id=session['emp_id']).first()
    return profile, current_address, permanent_address, doc_cv, email, phone, doc_tazkira, doc_guarantor, doc_tin, doc_education, doc_extra


def get_documents(emp_id):
    cv_doc = Documents.query.filter_by(emp_id=emp_id, name="cv").first()
    guarantor_doc = Documents.query.filter_by(emp_id=emp_id, name="guarantor").first()
    tazkira_doc = Documents.query.filter_by(emp_id=emp_id, name="tazkira").first()
    education_doc = Documents.query.filter_by(emp_id=emp_id, name="education").first()
    tin_doc = Documents.query.filter_by(emp_id=emp_id, name="tin").first()
    extra_doc = Documents.query.filter_by(emp_id=emp_id, name="extra").first()
    return cv_doc, guarantor_doc, tin_doc, education_doc, extra_doc, tazkira_doc


def uploadProfilePic(request):
    request_file = request.files['profilePic']
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    ext = request_file.filename.split('.')[1]
    if ext in ALLOWED_EXTENSIONS:
        request_file.filename = f"profile-" + session['emp_id'] +"."+ext
        workingdir = os.path.abspath(os.getcwd())
        path = os.path.join(workingdir+"/rpc_package/static/images/profiles", request_file.filename)
        print(workingdir)
        emp = Employees.query.filter_by(id=session['emp_id']).first()
        emp.profile_pic=f"/static/images/profiles/" + request_file.filename
        assert isinstance(db, object)
        request_file.save(path)
        db.session.commit()
        return 'success'
    else:
        return "invalid extention"