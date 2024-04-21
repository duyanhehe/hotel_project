from flask import Flask, render_template, flash, request, url_for, redirect, session
import dbModel, mysql.connector
from mysql.connector import Error
from markupsafe import escape
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldjfasduosadfupoas'

# Check Login
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_login' in session:
            return f(*args, **kwargs)
        else:            
            print("You need to login first")
            return render_template('user/auth/login.html', error='You need to login first')    
    return wrap

# USER
@app.route('/')
def homepage():
    active_page = 'home'
    email = ''
    if 'email' in session and 'is_login' in session and session['is_login']:
        email = session['email']
    return render_template("home.html", active_page = active_page, email = email)

@app.route('/booking')
def hotel_page():
    active_page = 'hotel'
    hotel = dbModel.Hotel()
    hotels = hotel.getAll()
    # print(hotels)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("booking/hotel.html", active_page = active_page, email = email, hotels = hotels)

@app.route('/booking/<hotel_id>')
def room_page():
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
            user = user_model.getByEmail(email)
            print("Session variables set:", session)  # Add this line to check session variables
            print(user)
            print(user[6])
            if user[6]=='standard':
                return redirect(url_for('homepage'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Wrong email or password', category='error')
    return render_template("user/auth/login.html") 

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
        captcha_input = request.form.get('captcha')
        agree_terms = request.form.get('agree_terms')
        
        uniqueFlag = True
        user_model = dbModel.User()

        user = dict()
        user['email'] = request.form['email']
        user['firstName'] = request.form['firstName']
        user['lastName'] = request.form['lastName']
        user['phoneNumber'] = request.form['phoneNumber']
        # Check if email is empty or already exists in the database
        if user['email'] == '' or user_model.getByEmail(user['email']):
            uniqueFlag = False
        if request.form['password']!='' and password == password1:
            user['password'] = password
        else:
            user['password']=''
        user['usertype'] = 'standard'

        
        # Add new user if all conditions are met
        if uniqueFlag and  user['password']!='' and captcha_input == session['captcha']:
            user_model = dbModel.User()
            if user_model.addNew(user):
                return redirect(url_for('login'))     

        # Flash error if the requirements are not met
        if len(email) < 4:
            flash('Email must be at least 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be at least 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be at least 1 character.', category='error')
        elif not phoneNumber.replace('+','').isdigit():
            flash('Phone number only contain numbers.', category='error')
        elif len(phoneNumber) > 8:
            flash('Phone number must be at least 9 characters.', category='error')
        elif len(password) > 7:
            flash('Password must be at least 8 characters', category='error')
        elif password != password1:
            flash('Password don\'t match.', category='error')
        elif captcha_input != session['captcha']:
            flash('CAPTCHA incorrect. Please try again.', category='error')
        elif not agree_terms:
            flash('Please agree to the terms of service.', category='error')
        else:
            flash('Account created!', category='success')

    session['captcha'] = dbModel.generate_captcha()     # Generaate CAPTCHA
    return render_template("user/auth/sign_up.html", captcha=session['captcha'])

@app.route('/terms_of_services')
def terms_of_services():
    return render_template("user/auth/ToS.html")

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
    return render_template("user/auth/forgot_pass.html")

@app.route('/edit_payment')
@login_required
def edit_payment():
    return render_template("user/edit_payment.html")

# ADMIN
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template("admin/dashboard.html")

@app.route('/admin/booking/all_bookings')
@login_required
def all_bookings():
    return render_template("admin/booking/all_bookings.html")

@app.route('/admin/booking/add_booking')
@login_required
def add_booking():
    return render_template("admin/booking/add_booking.html")

@app.route('/admin/booking/edit_booking')
@login_required
def edit_booking():
    return render_template("admin/booking/edit_booking.html")

@app.route('/admin/room/all_rooms')
@login_required
def all_rooms():
    return render_template("admin/room/all_rooms.html")

@app.route('/admin/payment')
@login_required
def payment_methods():
    return render_template('admin/payment/methods.html')

@app.route('/admin/customers/list')
@login_required
def customers_list():
    customer = dbModel.User()
    users = customer.getAll()
    # print(users)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template('admin/customers/list.html', email = email, users = users)

@app.route('/admin/customers/<users_id>')
@login_required
def customers_details(users_id):
    customer = dbModel.User()
    user_detail = customer.getById(users_id)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template('admin/customers/view.html', user = user_detail, email = email)

@app.route('/admin/customers/edit/<users_id>', methods=['GET', 'POST'])
@login_required
def customers_edit(users_id):
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    customer = dbModel.User()
    if request.method == "POST":
        user = dict()
        user['users_id'] = users_id
        user['email'] = request.form['email'] if request.form['email'] != '' else ''
        user['firstName'] = request.form['firstName'] if request.form['firstName'] != '' else ''
        user['lastName'] = request.form['lastName'] if request.form['lastName'] != '' else ''
        user['password'] = request.form['password'] if request.form['password'] != '' else ''
        user['usertype'] = request.form['usertype'] if request.form['usertype'] != '' else ''

        if customer.update_user(user):
            print('Update successfully')
            return redirect(url_for('customers_details', users_id = user['users_id']), email = email)
        else:
            print('Error')
            print(user)
            return redirect(url_for('customers_edit', users_id = user['users_id']), email = email)
    else:
        users = customer.getById(users_id)
    return render_template('admin/customers/edit.html', user = users, email = email)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)