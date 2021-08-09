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
    form_obj.tazkira.label.text = translation_obj.tazkira[language]
    form_obj.birthday.label.text = translation_obj.date_of_birth[language]
    form_obj.gender.label.text = translation_obj.gender[language]
    form_obj.gender.choices[0][1] = translation_obj.male[language]
    form_obj.gender.choices[1][1] = translation_obj.female[language]
    form_obj.m_status.label.text = translation_obj.status[language]
    form_obj.m_status.choices[0][1] = translation_obj.married[language]
    form_obj.m_status.choices[1][1] = translation_obj.single[language]
    form_obj.email.label.text = translation_obj.email[language]
    form_obj.email_second.label.text = translation_obj.email_second[language]
    form_obj.phone_second.label.text = translation_obj.phone_second[language]
    form_obj.phone.label.text = translation_obj.phone[language]
    form_obj.permanent_address.label.text = translation_obj.permanent_address[language]
    form_obj.current_address.label.text = translation_obj.current_address[language]
    form_obj.provinces_permanent.label.text = translation_obj.provinces[language]
    form_obj.provinces_current.label.text = translation_obj.provinces[language]
    form_obj.district_permanent.label.text = translation_obj.district[language]
    form_obj.district_current.label.text = translation_obj.district[language]
    form_obj.submit.label.text = translation_obj.add_new_employee[language]
    return form_obj


def update_messages_leave(form_obj, language):
    form_obj.leave_type.choices[0][1] = translation_obj.hourly[language]
    form_obj.leave_type.choices[1][1] = translation_obj.daily[language]
    form_obj.leave_type.label.text = translation_obj.leave_type[language]
    form_obj.submit.label.text = translation_obj.send_request[language]
    form_obj.start_datetime.label.text = translation_obj.start_date[language]
    form_obj.end_datetime.label.text = translation_obj.end_date[language]
    return form_obj





