from rpc_package import translation_obj, message_obj


def update_messages_user(form_obj, language):
    """
    This function is created for translation of user form in two languages (dari and english) that have two argument
    first is form_obj that get from forms.py and second is language that get from dari_english_translation.js 

    Args:
        form_obj (form): The type of this variable is form and name of this variable from forms.py
        language (string): The type of this variable is string and get value from dari_english_translation.js

    Returns:
        form: return value of variable in each language that we want
    """
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
    """
    This function is created for translation of employee form in two languages (dari and english) that have two argument
    first is form_obj that get from forms.py and second is language that get from dari_english_translation.js 
    
    Args:
        form_obj (form): The type of this variable is form and name of this variable from forms.py
        language (string): The type of this variable is string and get value from dari_english_translation.js

    Returns:
        form: return value of variable in each language that we want
    """

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
    """
    This function is created for translation of leave form in two languages (dari and english) that have two argument
    first is form_obj that get from forms.py and second is language that get from dari_english_translation.js 

    Args:
        form_obj (form): The type of this variable is form and name of this variable from forms.py
        language (string): The type of this variable is string and get value from dari_english_translation.js

    Returns:
        form: return value of variable in each language that we want
    """
    form_obj.name_department.label.text = translation_obj.name_department[language]
    form_obj.name_english_department.label.text = translation_obj.name_english_department[language]
    form_obj.submit.label.text = translation_obj.send_request[language]
    return form_obj


def update_messages_overtime(form_obj, language):
    form_obj.overtime_type.choices[0][1] = translation_obj.hourly[language]
    form_obj.overtime_type.choices[1][1] = translation_obj.daily[language]
    form_obj.overtime_type.label.text = translation_obj.overtime_type[language]
    form_obj.description.label.text = translation_obj.overtime_description[language]
    form_obj.submit.label.text = translation_obj.send_request[language]
    form_obj.start_datetime.label.text = translation_obj.start_date[language]
    form_obj.end_datetime.label.text = translation_obj.end_date[language]
    return form_obj

def update_messages_loan(form_obj, language):
    form_obj.requested_amount.label.text = translation_obj.requested_amount[language]
    form_obj.guarantor.label.text = translation_obj.guarantor[language]
    form_obj.submit.label.text = translation_obj.send_request[language]
    form_obj.start_date.label.text = translation_obj.repayment_start_date[language]
    form_obj.end_date.label.text = translation_obj.repayment_end_date[language]
    return form_obj


def update_messages_resign(form_obj, language):
    """
    This function is created for translation of leave form in two languages (dari and english) that have two argument
    first is form_obj that get from forms.py and second is language that get from dari_english_translation.js 

    Args:
        form_obj (form): The type of this variable is form and name of this variable from forms.py
        language (string): The type of this variable is string and get value from dari_english_translation.js

    Returns:
        form: return value of variable in each language that we want
    """
    form_obj.reason.label.text = translation_obj.resign_reason[language]
    form_obj.submit.label.text = translation_obj.send_request[language]
    form_obj.responsibilities.label.text = translation_obj.responsibilities[language]
    form_obj.equipments.label.text = translation_obj.equipments[language]
    return form_obj


def update_messages_department(form_obj, language):
    """
    This function is created for translation of leave form in two languages (dari and english) that have two argument
    first is form_obj that get from forms.py and second is language that get from dari_english_translation.js 

    Args:
        form_obj (form): The type of this variable is form and name of this variable from forms.py
        language (string): The type of this variable is string and get value from dari_english_translation.js

    Returns:
        form: return value of variable in each language that we want
    """
    form_obj.name_department.label.text = translation_obj.name_department[language]
    form_obj.name_english_department.label.text = translation_obj.name_english_department[language]
    form_obj.submit.label.text = translation_obj.send_request[language]
    return form_obj
