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
    return userPage(userName) if userName in usersData else 'Error'


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
    usersData[userName] = [password, dateBorn, {'expenses': [[], []], 'income': [[], []]}]
    with open('Users/UsersData.json', 'w') as users:
        dump(usersData, users, ensure_ascii=False, indent='\t')
    return userPage(userName)


@application.route('/userPage/<UserName>')
def userPage(UserName: str):
    with open('Users/UsersData.json', 'r') as users:
        usersData = load(users)
    userData = usersData[UserName][-1]
    chart_data = [userData[i] for i in userData]
    return render_template('userPage.html',
                           chart_data=chart_data,
                           expensesLink=f'/userPage/{UserName}/Расходы',
                           incomeLink=f'/userPage/{UserName}/Доходы')


@application.route('/userPage/<UserName>/<formForGraph>')
def formPage(UserName: str, formForGraph: str):
    return render_template('expenses_income.html',
                           operationName=formForGraph,
                           homeUserLink=f'/userPage/{UserName}')


if __name__ == '__main__':
    application.run(debug=True)
