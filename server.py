import flask.wrappers
import numpy as np
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from json import load, dump
import pandas as pd
from Bank import CurrencyExchanger
from datetime import date, timedelta
import calendar
from PredictMonyeModel import LinearModel


UPLOAD_FOLDER = 'Users/Datas'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}


application = Flask(__name__, template_folder='templates')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

bank = CurrencyExchanger(currency=['USD', 'EUR', 'CNY'])
model = LinearModel()


def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getPridiction(UserName: str):
    with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
        userData = load(users)[UserName][-1]
    current_date = date.today()
    dataColumns = {
        'year': [],
        'month': [],
        'day': [],
        'monye': [],
        'income_or_expenses': [],
        'USD': [],
        'EUR': [],
        'CNY': []
    }
    resData = {
        'timeInterval': [],
        'income': [],
        'expenses': []
    }
    if any([len(userData[elem]) > 0 for elem in userData]):
        for i in userData:
            for elem in sorted(userData[i]):
                year, month, day = map(int, elem.split('-'))
                dataColumns['year'].append(year)
                dataColumns['month'].append(month)
                dataColumns['day'].append(day)
                dataColumns['monye'].append(userData[i][elem][0])
                dataColumns['income_or_expenses'].append(1 if i == 'income' else 0)
                dataColumns['USD'].append(userData[i][elem][1])
                dataColumns['EUR'].append(userData[i][elem][2])
                dataColumns['CNY'].append(userData[i][elem][-1])
        data = pd.DataFrame(dataColumns)
        X = data.drop(columns=['monye'])
        Y = data['monye']

        pred_date_day = current_date + timedelta(days=1)
        pred_date_week = current_date + timedelta(days=7)

        month_calc = calendar.monthrange(current_date.year, current_date.month)[1]
        pred_date_month = current_date + timedelta(days=month_calc)

        for pred_date in [pred_date_day, pred_date_week, pred_date_month]:
            X_prediction = pd.DataFrame(
                {
                    'year': [pred_date.year, pred_date.year],
                    'month': [pred_date.month, pred_date.month],
                    'day': [pred_date.day, pred_date.day],
                    'income_or_expenses': [1, 0],
                    'USD': [np.mean(X['USD']), np.mean(X['USD'])],
                    'EUR': [np.mean(X['EUR']), np.mean(X['EUR'])],
                    'CNY': [np.mean(X['CNY']), np.mean(X['CNY'])]
                }
            )
            resData['timeInterval'].append(pred_date)
            resData['income'].append(model.fit_predict(X=X, Y=Y, X_prediction=X_prediction.iloc[0:1, :]))
            resData['expenses'].append(model.fit_predict(X=X, Y=Y, X_prediction= X_prediction.iloc[1:, :]))
        return pd.DataFrame(resData)
    return pd.DataFrame(resData)


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
    print(usersData)
    if userName in usersData:
        if usersData[userName][1] == password:
            return userPage(userName)
        else:
            return 'warning password'
    return 'warning user name'


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
        [userData['expenses'][i][0] for i in sorted(userData['expenses'])],
        sorted(userData['expenses'])
    ]
    chart_income_data = [
        [userData['income'][i][0] for i in sorted(userData['income'])],
        sorted(userData['income'])
    ]
    chart_ratio_data = [sum(chart_expenses_data[0]), sum(chart_income_data[0])]

    dataPrediction = getPridiction(UserName)

    return render_template(
        'userPage.html',
        chart_expenses_data=chart_expenses_data,
        chart_income_data=chart_income_data,
        chart_ratio_data=chart_ratio_data,
        expensesLink=f'/userPage/{UserName}/Расходы',
        incomeLink=f'/userPage/{UserName}/Доходы',
        getDataUser=f'/getDataUser/{UserName}',
        setDataUser=f'/setDataUser/{UserName}',
        dataPrediction=[dataPrediction.iloc[elem, :].values for elem in range(3)] if dataPrediction.index.stop else []
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
        ][userForm['dateAction']][0] += int(userForm['monyeAction'])
    else:
        usersData[UserName][-1][
            'expenses' if formForGraph == 'Расходы' else 'income'
        ][userForm['dateAction']] = [int(userForm['monyeAction'])] + [i for i in
                                                                      bank.exchange(date=userForm['dateAction'])]
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
            'income_or_expenses': [],
            'USD': [],
            'EUR': [],
            'CNY': []
        }
        for i in userData:
            for date in sorted(userData[i]):
                dataColumns['date'].append(date)
                dataColumns['monye'].append(userData[i][date][0])
                dataColumns['income_or_expenses'].append(i)
                dataColumns['USD'].append(userData[i][date][1])
                dataColumns['EUR'].append(userData[i][date][2])
                dataColumns['CNY'].append(userData[i][date][-1])
        data = pd.DataFrame(dataColumns)
    else:
        dataColumns = {
            'date': [],
            'monye': [],
            'USD': [],
            'EUR': [],
            'CNY': []
        }
        for date in sorted(userData[variantData]):
            dataColumns['date'].append(date)
            dataColumns['monye'].append(userData[variantData][date])
            dataColumns['USD'].append(userData[variantData][date][1])
            dataColumns['EUR'].append(userData[variantData][date][2])
            dataColumns['CNY'].append(userData[variantData][date][-1])
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
                if data.iloc[i, 0] in userData[UserName][-1][data.iloc[i, 2]]:
                    userData[UserName][-1][data.iloc[i, 2]][data.iloc[i, 0]][0] = (
                            userData[UserName][-1][data.iloc[i, 2]][data.iloc[i, 0]][0] + int(data.iloc[i, 1]))
                else:
                    userData[UserName][-1][data.iloc[i, 2]][data.iloc[i, 0]] = ([int(data.iloc[i, 1])]
                                                                                 + [i for i in
                                                                                    bank.exchange(date=data.iloc[i, 0])
                                                                                    ])

        else:
            for i in range(len(data)):
                if data.iloc[i, 0] in userData[UserName][-1][variantData]:
                    userData[UserName][-1][variantData][data.iloc[i, 0]][0] = (
                            userData[UserName][-1][variantData][data.iloc[i, 0]][0] + int(data.iloc[i, 1]))
                else:
                    userData[UserName][-1][variantData][data.iloc[i, 0]] = ([int(data.iloc[i, 1])]
                                                                            + [i for i in
                                                                               bank.exchange(date=data.iloc[i, 0])
                                                                               ])

        with open('Users/UsersData.json', 'w', encoding='utf-8') as users:
            dump(
                userData,
                users,
                ensure_ascii=False,
                indent='\t'
            )

        return userPage(UserName)


# @application.route('/getPrediction/<UserName>/<time_interval>/<income_or_expenses>')
# def getPridiction_url(UserName: str, time_interval: str, income_or_expenses: int):
#     with open('Users/UsersData.json', 'r', encoding='utf-8') as users:
#         userData = load(users)[UserName][-1]
#     current_date = date.today()
#     if time_interval == 'day':
#         dataColumns = {
#             'year': [],
#             'month': [],
#             'day': [],
#             'monye': [],
#             'income_or_expenses': [],
#             'USD': [],
#             'EUR': [],
#             'CNY': []
#         }
#         for i in userData:
#             for elem in sorted(userData[i]):
#                 year, month, day = map(int, elem.split('-'))
#                 dataColumns['year'].append(year)
#                 dataColumns['month'].append(month)
#                 dataColumns['day'].append(day)
#                 dataColumns['monye'].append(userData[i][elem][0])
#                 dataColumns['income_or_expenses'].append(1 if i == 'income' else 0)
#                 dataColumns['USD'].append(userData[i][elem][1])
#                 dataColumns['EUR'].append(userData[i][elem][2])
#                 dataColumns['CNY'].append(userData[i][elem][-1])
#         data = pd.DataFrame(dataColumns)
#         X = data.drop(columns=['monye'])
#         Y = data['monye']
#         pred_date = current_date + timedelta(days=1)
#         X_prediction = pd.DataFrame(
#             {
#                 'year': [pred_date.year],
#                 'month': [pred_date.month],
#                 'day': [pred_date.day],
#                 'income_or_expenses': [income_or_expenses],
#                 'USD': [np.mean(X['USD'])],
#                 'EUR': [np.mean(X['EUR'])],
#                 'CNY': [np.mean(X['CNY'])]
#             }
#         )
#         return str(model.fit_predict(X=X, Y=Y, X_prediction=X_prediction))
#     if time_interval == 'week':
#         dataColumns = {
#             'year': [],
#             'month': [],
#             'day': [],
#             'monye': [],
#             'income_or_expenses': [],
#             'USD': [],
#             'EUR': [],
#             'CNY': []
#         }
#         for i in userData:
#             for elem in sorted(userData[i]):
#                 year, month, day = map(int, elem.split('-'))
#                 dataColumns['year'].append(year)
#                 dataColumns['month'].append(month)
#                 dataColumns['day'].append(day)
#                 dataColumns['monye'].append(userData[i][elem][0])
#                 dataColumns['income_or_expenses'].append(1 if i == 'income' else 0)
#                 dataColumns['USD'].append(userData[i][elem][1])
#                 dataColumns['EUR'].append(userData[i][elem][2])
#                 dataColumns['CNY'].append(userData[i][elem][-1])
#         data = pd.DataFrame(dataColumns)
#         X = data.drop(columns=['monye'])
#         Y = data['monye']
#         pred_date = current_date + timedelta(days=7)
#         X_prediction = pd.DataFrame(
#             {
#                 'year': [pred_date.year],
#                 'month': [pred_date.month],
#                 'day': [pred_date.day],
#                 'income_or_expenses': [income_or_expenses],
#                 'USD': [np.mean(X['USD'])],
#                 'EUR': [np.mean(X['EUR'])],
#                 'CNY': [np.mean(X['CNY'])]
#             }
#         )
#         return str(model.fit_predict(X=X, Y=Y, X_prediction=X_prediction))
#     if time_interval == 'month':
#         dataColumns = {
#             'year': [],
#             'month': [],
#             'day': [],
#             'monye': [],
#             'income_or_expenses': [],
#             'USD': [],
#             'EUR': [],
#             'CNY': []
#         }
#         for i in userData:
#             for elem in sorted(userData[i]):
#                 year, month, day = map(int, elem.split('-'))
#                 dataColumns['year'].append(year)
#                 dataColumns['month'].append(month)
#                 dataColumns['day'].append(day)
#                 dataColumns['monye'].append(userData[i][elem][0])
#                 dataColumns['income_or_expenses'].append(1 if i == 'income' else 0)
#                 dataColumns['USD'].append(userData[i][elem][1])
#                 dataColumns['EUR'].append(userData[i][elem][2])
#                 dataColumns['CNY'].append(userData[i][elem][-1])
#         data = pd.DataFrame(dataColumns)
#         X = data.drop(columns=['monye'])
#         Y = data['monye']
#         month_calc = calendar.monthrange(current_date.year, current_date.month)[1]
#         pred_date = current_date + timedelta(days=month_calc)
#         X_prediction = pd.DataFrame(
#             {
#                 'year': [pred_date.year],
#                 'month': [pred_date.month],
#                 'day': [pred_date.day],
#                 'income_or_expenses': [income_or_expenses],
#                 'USD': [np.mean(X['USD'])],
#                 'EUR': [np.mean(X['EUR'])],
#                 'CNY': [np.mean(X['CNY'])]
#             }
#         )
#         return str(model.fit_predict(X=X, Y=Y, X_prediction=X_prediction))


if __name__ == '__main__':
    application.run(debug=True)
