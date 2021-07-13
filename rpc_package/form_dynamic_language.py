from rpc_package import translation_obj, message_obj


def update_messages_user(form_obj, language):
    form_obj.employee_id.label.text = translation_obj.employee_id[language]
    form_obj.employee_id.validators[2].message = message_obj.wrong_format[language].format("Employee ID")
    form_obj.password.label.text = translation_obj.password[language]
    form_obj.password.validators[1].message = message_obj.check_length[language].format(str(6), "")
    form_obj.confirm_password.label.text = translation_obj.confirm_password[language]
    form_obj.confirm_password.validators[1].message = message_obj.equal[language]
    form_obj.user_role.label.text = translation_obj.user_role[language]
    form_obj.submit.label.text = translation_obj.submit_user[language]
    form_obj.employee_id.validators[1].message = message_obj.check_length[language].format(str(8), "Employee ID")
    return form_obj


def update_messages_employee(form_obj, language):
    form_obj.employee_id.label.text = translation_obj.employee_id[language]
    form_obj.employee_id.validators[2].message = message_obj.wrong_format[language].format("Employee ID")
    form_obj.first_name.label.text = translation_obj.name[language]
    form_obj.last_name.label.text = translation_obj.last_name[language]
    form_obj.father_name.label.text = translation_obj.father_name[language]
    return form_obj




