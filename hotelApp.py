from flask import Flask, render_template, flash, request, url_for, redirect, session
import dbModel, mysql.connector
from mysql.connector import Error
from markupsafe import escape
from functools import wraps
from datetime import datetime

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
    
    # Get all hotels
    hotel = dbModel.Hotel()
    hotels = hotel.getAll()
    
    # Get distinct cities
    cities = hotel.getDistinctCities()
    
    email = session['email'] if 'email' in session and session['email'] != '' else ''
    
    return render_template("booking/hotel.html", active_page=active_page, email=email, hotels=hotels, cities=cities)

@app.route('/booking/<int:hotel_id>')
def room_page(hotel_id):
    active_page = 'hotel'
    room = dbModel.Room()
    rooms = room.getAll(hotel_id)

    hotel = dbModel.Hotel()
    hotels = hotel.getAll()
    email = session['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("booking/room.html", active_page=active_page, email=email, rooms=rooms, hotels=hotels)

@app.route('/booking/<int:hotel_id>/confirm_booking/<int:room_id>', methods=['GET', 'POST'])
def confirm_booking(hotel_id, room_id):
    booking_model = dbModel.Booking()
    booking_details = booking_model.getDetailById(room_id, hotel_id)
    # print(booking)
    if request.method == 'POST':
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        booking_date = datetime.now().date()
        users_id = session['users_id'] if 'users_id' in session else None
        # Calculate total price
        booking = {
            'users_id': users_id,
            'room_id': room_id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'booking_date': datetime.now().date()
        }
        success, total_price = booking_model.calculate_total_price(booking)
        if success:
            return redirect(url_for('homepage'))
        else:
            return redirect(url_for('room_page'))

    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("booking/confirm_booking.html", email = email, booking_details = booking_details)


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
            session['usertype'] = user[6]
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

# ADMIN
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    customer = dbModel.User()
    users = customer.getAll(5)
    # print(users)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/dashboard.html", email = email, users = users)

@app.route('/admin/booking/all_bookings')
@login_required
def all_bookings():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    booking = dbModel.Booking()
    all_bookings = booking.getAll()
    # print(all_bookings)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/booking/all_bookings.html", email = email, all_bookings = all_bookings)

@app.route('/admin/booking/add')
@login_required
def add_booking():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    return render_template("admin/booking/add.html")

@app.route('/admin/booking/edit')
@login_required
def edit_booking():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    return render_template("admin/booking/edit.html")

@app.route('/admin/all_hotels', methods=['GET', 'POST'])
@login_required
def all_hotels():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    hotel = dbModel.Hotel()
    hotels = hotel.getAll()
    # print(hotels)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    if request.method == 'POST':
        delete_hotel = request.form.get('delete_hotel')
        print("Deleting hotel with ID:", delete_hotel)
        hotel.delete(delete_hotel)
    return render_template("admin/room/hotel_list.html", email = email, hotels = hotels)

@app.route('/admin/room_list/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def room_list(hotel_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    room = dbModel.Room()
    rooms = room.getAll(hotel_id)

    hotel = dbModel.Hotel()
    hotels = hotel.getAll()
    # print(hotel_detail)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    if request.method == 'POST':
        delete_room = request.form.get('delete_room')
        print("Deleting hotel with ID:", delete_room)
        hotel.delete_room(delete_room)

    return render_template("admin/room/room_list.html", email=email, rooms=rooms, hotels=hotels)

@app.route('/admin/payment')
@login_required
def payment_methods():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    return render_template('admin/payment/methods.html')

@app.route('/admin/customers/list', methods=['GET', 'POST'])
@login_required
def customers_list():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    customer = dbModel.User()
    users = customer.getAll()
    # print(users)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''

    if request.method == 'POST':
        delete_customer = request.form.get('delete_customer')
        # print("Deleting user with ID:", delete_customer)
        customer.delete(delete_customer)
    return render_template('admin/customers/list.html', email = email, users = users)

@app.route('/admin/customers/<users_id>')
@login_required
def customers_details(users_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    customer = dbModel.User()
    user_detail = customer.getDetailById(users_id)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template('admin/customers/view.html', user = user_detail, email = email)

@app.route('/admin/customers/edit/<users_id>', methods=['GET', 'POST'])
@login_required
def customers_edit(users_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    customer = dbModel.User()
    if request.method == "POST":
        user = dict()
        user['users_id'] = users_id
        user['email'] = request.form['email'] if request.form['email'] != '' else ''
        user['firstName'] = request.form['firstName'] if request.form['firstName'] != '' else ''
        user['lastName'] = request.form['lastName'] if request.form['lastName'] != '' else ''
        user['password'] = request.form['password'] if request.form['password'] != '' else ''
        user['phoneNumber'] = request.form['phoneNumber'] if request.form['phoneNumber'] != '' else ''
        user['usertype'] = request.form['usertype'] if request.form['usertype'] != '' else ''

        if customer.update_user(user):
            print('Update successfully')
            return redirect(url_for('customers_details', users_id = user['users_id']))
        else:
            print('Error')
            print(user)
            return redirect(url_for('customers_edit', users_id = user['users_id']))
    else:
        users = customer.getById(users_id)
    return render_template('admin/customers/edit.html', user = users, email = email)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)