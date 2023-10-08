import flask.wrappers
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from json import load, dump
import pandas as pd
import os


UPLOAD_FOLDER = 'Users/Datas'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}


application = Flask(__name__, template_folder='templates')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        getDataUser=f'/getDataUser/{UserName}',
        setDataUser=f'/setDataUser/{UserName}'
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
def getDataUser(UserName: str) -> str:
    return render_template(
        'getDataUsers.html',
        homeUserPage=f'/userPage/{UserName}',
        getDataLink=f'/getDataUser/Get/{UserName}'
    )


@application.route('/getDataUser/Get/<UserName>', methods=['POST'])
def downloadDataUser(UserName: str) -> flask.wrappers.Response:
    fileFormat, variantData = [request.form[elem] for elem in request.form]
    filename = UserName + '.' + fileFormat


    with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
        userData = load(users)[UserName][-1]

    if variantData == 'income_and_expenses':
        dataColumns = {
            'date': [],
            'monye': [],
            'income_or_expenses': []
        }
        for i in userData:
            for date in sorted(userData[i]):
                dataColumns['date'].append(date)
                dataColumns['monye'].append(int(userData[i][date]))
                dataColumns['income_or_expenses'].append(i)
        data = pd.DataFrame(dataColumns)
    else:
        dataColumns = {
            'date': [],
            'monye': []
        }
        for date in sorted(userData[variantData]):
            dataColumns['date'].append(date)
            dataColumns['monye'].append(int(userData[variantData][date]))
        data = pd.DataFrame(dataColumns)

    if fileFormat == 'csv':
        data.to_csv('Users/Datas/' + filename, index=False)
    else:
        data.to_excel('Users/Datas/' + filename, index=False)

    return send_from_directory(application.config["UPLOAD_FOLDER"], filename)


@application.route('/setDataUser/<UserName>')
def setDataUser(UserName: str) -> str:
    return render_template(
        'setDataUsers.html',
        homeUserPage=f'/userPage/{UserName}',
        setDataLink=f'/setDataUser/Set/{UserName}',
        setExamles='/setDataUser/Set/examples'
    )


@application.route('/setDataUser/Set/examples', methods=['GET'])
def downloadExaples_for_setDataUser():
    return send_from_directory(application.config["UPLOAD_FOLDER"], 'examples.zip')


@application.route('/setDataUser/Set/<UserName>', methods=['POST'])
def uploadDataUser(UserName: str):
    file = request.files['file']
    variantData = request.form['income_or_expenses']
    if not len(file.filename.split('.')[0]):
        return 'No selected file'
    if len(file.filename.split('.')[0]) and allowed_file(file.filename):
        fileName = secure_filename(file.filename)
        file.save(application.config['UPLOAD_FOLDER'] + '/' + fileName)

        with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
            userData = load(users)

        data = pd.read_csv(application.config['UPLOAD_FOLDER'] + '/' + fileName) if '.csv' in fileName\
            else pd.read_excel(application.config['UPLOAD_FOLDER'] + '/' + fileName)

        if variantData == 'income_and_expenses':
            for i in range(len(data)):
                if data.iloc[i, 0] in userData[UserName][-1][data.iloc[i, -1]]:
                    userData[UserName][-1][data.iloc[i, 1]][data.iloc[i, 0]] = str(
                        int(userData[UserName][-1][data.iloc[i, 1]][data.iloc[i, 0]]) + int(data.iloc[i, 1])
                    )
                else:
                    userData[UserName][-1][data.iloc[i, -1]][data.iloc[i, 0]] = str(data.iloc[i, 1])

        else:
            for i in range(len(data)):
                if data.iloc[i, 0] in userData[UserName][-1][variantData]:
                    userData[UserName][-1][variantData][data.iloc[i, 0]] = str(
                        int(userData[UserName][-1][variantData][data.iloc[i, 0]]) + int(data.iloc[i, 1])
                    )
                else:
                    userData[UserName][-1][variantData][data.iloc[i, 0]] = str(data.iloc[i, 1])

        with open('Users/UsersData.json', 'w', encoding='utf-8') as users:
            dump(
                userData,
                users,
                ensure_ascii=False,
                indent='\t'
            )

        return userPage(UserName)


if __name__ == '__main__':
    application.run(debug=True)
