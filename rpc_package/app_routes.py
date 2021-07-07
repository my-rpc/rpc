from flask import render_template, url_for, flash, redirect, request, jsonify
from rpc_package import app, translation_obj, message_obj
from rpc_package.forms import CreateUserForm, LoginForm
from wtforms.fields import Label


@app.route("/blank", methods=['GET', 'POST'])
def blank():
    return render_template('blank.html', language='en')


@app.route("/create_new_user", methods=['GET', 'POST'])
def create_new_user():
    language = 'en'
    create_new_user_form = CreateUserForm()
    if create_new_user_form.validate_on_submit():
        flash(message_obj.create_new_user_save[language].format(create_new_user_form.employee_id.data), 'success')
        return jsonify({'success':True, 'message': message_obj.create_new_user_save[language].format(create_new_user_form.employee_id.data)}), 200, {'ContentType':'application/json'} 
    else:
        if request.method == 'POST':
            flash(message_obj.create_new_user_not[language], 'danger')
            # return jsonify({'success':True, 'message': message_obj.create_new_user_save[language].format(create_new_user_form.employee_id.data)}), 403, {'ContentType':'application/json'} 

    
    
    create_new_user_form.employee_id.label.text = translation_obj.employee_id[language]
    create_new_user_form.password.label.text = translation_obj.password[language]
    create_new_user_form.confirm_password.label.text = translation_obj.confirm_password[language]
    create_new_user_form.user_role.label.text = translation_obj.user_role[language]
    create_new_user_form.submit.label.text = translation_obj.submit_user[language]
    return render_template('create_new_user.html', title='Create New User',
                           form=create_new_user_form, language=language, translation=translation_obj,
                           message_obj=message_obj)


@app.route("/user_login")
def login():
    login_form = LoginForm()

    return render_template('user_login.html', title='Login',
                           form=login_form, language='en', translation=translation_obj)
