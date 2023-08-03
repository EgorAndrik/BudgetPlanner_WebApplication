from flask import Flask, render_template, request
from json import load, dump


application = Flask(__name__, template_folder='templates')


@application.route('/')
def homePage():
    return render_template('index.html')


@application.route('/LogInPage')
def LogInPage():
    return render_template('loginIndex.html')


@application.route('/LogInPage/LogIn', methods=['POST'])
def LogIn():
    formData = request.form
    userName, password = [formData[i] for i in formData]
    with open('Users/UsersData.json', 'r') as users:
        usersData = load(users)
    return [userName, password] if userName in usersData else 'Error'


@application.route('/RegistrationPage')
def registrPage():
    return render_template('registrationIndex.html')


@application.route('/RegistrationPage/Registration', methods=['POST'])
def registr():
    formData = request.form
    userName, password, dateBorn = [formData[i] for i in formData]
    with open('Users/UsersData.json', 'r') as users:
        usersData = load(users)
    if userName in usersData:
        return 'Error'
    usersData[userName] = [password, dateBorn]
    with open('Users/UsersData.json', 'w') as users:
        dump(usersData, users, ensure_ascii=False, indent='\t')
    return [userName, password, dateBorn]


if __name__ == '__main__':
    application.run(debug=True)
