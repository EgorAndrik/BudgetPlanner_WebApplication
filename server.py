from flask import Flask, render_template, request


application = Flask(__name__, template_folder='templates')


@application.route('/')
def homePage():
    return render_template('index.html')


@application.route('/LogInPage')
def LogInPage():
    return render_template('loginIndex.html')


@application.route('/RegistrationPage')
def registrPage():
    return render_template('registrationIndex.html')


if __name__ == '__main__':
    application.run(debug=True)
