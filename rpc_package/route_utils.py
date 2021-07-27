import os

from rpc_package import db
from rpc_package.rpc_tables import Documents


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
        db.session.add(document)
        db.session.commit()
        return 'success'
    except IOError as io:
        return 'error'
