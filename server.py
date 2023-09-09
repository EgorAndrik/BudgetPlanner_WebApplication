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
    usersData[userName] = [password, dateBorn, {'expenses': {}, 'income': {}}]
    with open('Users/UsersData.json', 'w') as users:
        dump(usersData, users, ensure_ascii=False, indent='\t')
    return userPage(userName)


@application.route('/userPage/<UserName>')
def userPage(UserName: str):
    with open('Users/UsersData.json', 'r') as users:
        usersData = load(users)
    userData = usersData[UserName][-1]
    chart_expenses_data = [
        [int(userData['expenses'][i]) for i in sorted(userData['expenses'])],
        sorted(userData['expenses'])
    ]
    chart_income_data = [
        [int(userData['income'][i]) for i in sorted(userData['income'])],
        sorted(userData['income'])
    ]
    chart_ratio_data = [sum(chart_expenses_data[0]), sum(chart_income_data[0])]
    return render_template('userPage.html',
                           chart_expenses_data=chart_expenses_data,
                           chart_income_data=chart_income_data,
                           chart_ratio_data=chart_ratio_data,
                           expensesLink=f'/userPage/{UserName}/Расходы',
                           incomeLink=f'/userPage/{UserName}/Доходы')


@application.route('/userPage/<UserName>/<formForGraph>')
def formPage(UserName: str, formForGraph: str):
    return render_template('expenses_income.html',
                           operationName=formForGraph,
                           homeUserLink=f'/userPage/{UserName}',
                           linkForData=f'/userData/{UserName}/{formForGraph}')


@application.route('/userData/<UserName>/<formForGraph>', methods=['POST'])
def addUserData(UserName: str, formForGraph: str):
    with open('Users/UsersData.json', 'r') as users:
        usersData = load(users)
    userForm = request.form
    if userForm['dateAction'] in usersData[UserName][-1]['expenses' if formForGraph == 'Расходы' else 'income']:
        usersData[UserName][-1][
            'expenses' if formForGraph == 'Расходы' else 'income'
        ][userForm['dateAction']] += userForm['monye']
    else:
        usersData[UserName][-1][
            'expenses' if formForGraph == 'Расходы' else 'income'
        ][userForm['dateAction']] = userForm['monye']
    with open('Users/UsersData.json', 'w') as users:
        dump(usersData, users, ensure_ascii=False, indent='\t')
    return formPage(UserName, formForGraph)


if __name__ == '__main__':
    application.run(debug=True)
