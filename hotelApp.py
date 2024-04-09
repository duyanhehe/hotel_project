from flask import Flask, render_template, flash, request, url_for, redirect, session
import dbModel, mysql.connector
from mysql.connector import Error
from markupsafe import escape
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldjfasduosadfupoas'


@app.route('/')
def homepage():
    active_page = 'home'
    return render_template("home.html", active_page = active_page)

@app.route('/booking')
def booking_page():
    active_page = 'booking'
    return render_template("booking/booking.html", active_page = active_page)

@app.route('/booking/<int:room_id>')
def room():
    pass
    # return render_template("booking/room.html")

@app.route('/contact')
def contact_page():
    active_page = 'contact'
    return render_template("contact.html", active_page = active_page)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' and request.form['email'] != '':
        email = request.form['email']
        password = request.form['password']
        user_model = dbModel.User()
        if user_model.checkLogin(email, password):
            session['email'] = email
            session['is_login'] = True
            return redirect(url_for('homepage'))
        else:
            flash('Wrong xdd', category='error')
    return render_template("user/login.html") 

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_login', None)
    session.clear()
    return redirect(url_for('homepage'))

@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        phoneNumber = request.form.get('phoneNumber')
        password = request.form.get('password')
        password1 = request.form.get('password1')
        
        uniqueFlag = True
        user_model = dbModel.User()

        user = dict()
        user['email'] = request.form['email']
        user['firstName'] = request.form['firstName']
        user['lastName'] = request.form['lastName']
        user['phoneNumber'] = request.form['phoneNumber']
        if user['email'] == '' or user_model.getByEmail(user['email']):
            uniqueFlag = False
        if request.form['password']!='' and password == password1:
            user['password'] = password
        else:
            user['password']=''
        user['usertype'] = ''
        if uniqueFlag and  user['password']!='':
            user_model = dbModel.User()
            if user_model.addNew(user):
                return redirect(url_for('login'))     
        # print(user)
        # Flash error if the requirements are not met
        if len(email) < 4:
            flash('Email must be at least than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be at least 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be at least than 1 character.', category='error')
        elif password != password1:
            flash('Password don\'t match.', category='error')
        elif len(password) > 7:
            flash('Password must be at least 8 characters', category='error')
        elif not phoneNumber.replace('+','').isdigit():
            flash('Phone number only contain numbers.', category='error')
        elif len(phoneNumber) < 10:
            flash('Phone number must be at least 9 characters.', category='error')
        else:
            flash('Account created!', category='success')

    return render_template("user/sign_up.html")


# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run()