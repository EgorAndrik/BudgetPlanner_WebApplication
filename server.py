from flask import Flask, render_template, request, send_from_directory
from json import load, dump


application = Flask(__name__, template_folder='templates')


# @application.route('/test/<filename>')
# def testDownload(filename):
    # return send_from_directory('Users', filename) # csv xlsx xls


@application.route('/')
def homePage() -> str:
    return render_template('index.html')


@application.route('/LogInPage')
def LogInPage() -> str:
    return render_template('loginIndex.html')


@application.route('/LogInPage/LogIn', methods=['POST'])
def LogIn() -> str:
    formData = request.form
    userName, password = [formData[i] for i in formData]
    with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
        usersData = load(users)
    return userPage(userName) if userName in usersData else 'Error'


@application.route('/RegistrationPage')
def registrPage() -> str:
    return render_template('registrationIndex.html')


@application.route('/RegistrationPage/Registration', methods=['POST'])
def registr() -> str:
    formData = request.form
    userName, password, dateBorn = [formData[i] for i in formData]
    with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
        usersData = load(users)
    if userName in usersData:
        return 'Error'
    usersData[userName] = [
        password,
        dateBorn,
        {
            'expenses': {},
            'income': {}
        }
    ]
    with open('Users/UsersData.json', 'w', encoding='utf-8') as users:
        dump(usersData, users, ensure_ascii=False, indent='\t')
    return userPage(userName)


@application.route('/userPage/<UserName>')
def userPage(UserName: str) -> str:
    with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
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
    return render_template(
        'userPage.html',
        chart_expenses_data=chart_expenses_data,
        chart_income_data=chart_income_data,
        chart_ratio_data=chart_ratio_data,
        expensesLink=f'/userPage/{UserName}/Расходы',
        incomeLink=f'/userPage/{UserName}/Доходы',
        getDataUser=f'/getDataUser/{UserName}'
    )


@application.route('/userPage/<UserName>/<formForGraph>')
def formPage(UserName: str, formForGraph: str) -> str:
    return render_template(
        'expenses_income.html',
        operationName=formForGraph,
        homeUserLink=f'/userPage/{UserName}',
        linkForData=f'/userData/{UserName}/{formForGraph}'
    )


@application.route('/userData/<UserName>/<formForGraph>', methods=['POST'])
def addUserData(UserName: str, formForGraph: str) -> str:
    with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
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
    with open('Users/UsersData.json', 'w', encoding='utf-8') as users:
        dump(
            usersData,
            users,
            ensure_ascii=False,
            indent='\t'
        )
    return formPage(UserName, formForGraph)


@application.route('/getDataUser/<UserName>')
def getDataUser(UserName: str):
    return render_template(
        'getDataUsers.html',
        homeUserPage=f'/userPage/{UserName}'
    )


if __name__ == '__main__':
    application.run(debug=True)
