from flask import render_template, url_for, flash, redirect, request, jsonify
from rpc_package import app, translation_obj
from rpc_package.forms import CreateUserForm, LoginForm
from wtforms.fields import Label


@app.route("/blank", methods=['GET', 'POST'])
def blank():
    return render_template('blank.html', language='en')


@app.route("/create_new_user")
def create_new_user():
    language = 'dari'
    create_new_user_form = CreateUserForm()
    create_new_user_form.employee_id.label.text = translation_obj.employee_id[language]
    create_new_user_form.password.label.text = translation_obj.password[language]
    create_new_user_form.confirm_password.label.text = translation_obj.confirm_password[language]
    create_new_user_form.user_role.label.text = translation_obj.user_role[language]
    create_new_user_form.submit.label.text = translation_obj.submit_user[language]
    return render_template('create_new_user.html', title='Create New User',
                           form=create_new_user_form, language=language, translation=translation_obj)


@app.route("/user_login")
def login():
    login_form = LoginForm()

    return render_template('user_login.html', title='Login',
                           form=login_form, language='en', translation=translation_obj)
