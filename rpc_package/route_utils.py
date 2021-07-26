import os

from rpc_package import db
from rpc_package.rpc_tables import Documents


def upload_docs(emp_id, request, file_type):
    request_file = request.files[file_type]
    request_file.filename = "Guarantor-" + emp_id + ".pdf"
    path = os.path.join(f"./rpc_package/static/files/{file_type}", request_file.filename)
    document = Documents(
        emp_id=emp_id,
        name="guarantor",
        url="/static/files/guarantor/" + request_file.filename)
    assert isinstance(db, object)
    db.session.add(document)
    db.session.commit()
    request_file.save(path)
