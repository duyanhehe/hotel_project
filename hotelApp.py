from flask import Flask, render_template, flash, request, url_for, redirect, session
import dbModel, mysql.connector
from mysql.connector import Error
from markupsafe import escape
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldjfasduosadfupoas'

# USER
@app.route('/')
def homepage():
    active_page = 'home'
    return render_template("home.html", active_page = active_page)

@app.route('/booking')
def booking_page():
    active_page = 'booking'
    return render_template("booking/booking.html", active_page = active_page)

@app.route('/booking/1')
def room():
    return render_template("booking/room.html")

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
            flash('Wrong email or password', category='error')
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
            flash('Email must be at least 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be at least 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be at least 1 character.', category='error')
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

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password1 = request.form['password1']

        if password != password1:
            flash('Password don\'t match.', category='error')
            return redirect(url_for('forgot_password'))

        user_model = dbModel.User()
        if user_model.getByEmail(email):
            if user_model.reset_password(email, password):
                #redirect or render a success message
                flash("Password reset successful", category='success')
                return redirect(url_for('login'))
            else:
                flash("Failed to reset password. Please try again", category='error')
                return redirect(url_for('forgot_password'))
        flash('Email address not found', category='error')
    return render_template("user/forgot_pass.html")


# ADMIN
@app.route('/admin')
def admin_login():
    return render_template("admin/login.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template("admin/dashboard.html")

@app.route('/admin/booking/all_bookings')
def all_bookings():
    return render_template("admin/booking/all_bookings.html")

@app.route('/admin/booking/add_booking')
def add_booking():
    return render_template("admin/booking/add_booking.html")

@app.route('/admin/booking/edit_booking')
def edit_booking():
    return render_template("admin/booking/edit_booking.html")

@app.route('/admin/room/all_rooms')
def all_rooms():
    return render_template("admin/room/all_rooms.html")

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)