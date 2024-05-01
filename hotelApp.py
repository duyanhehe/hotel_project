"""
TEAM MEMBERS
- Tran Duy Anh
- Nguyen Quang Manh
- Bui Vu Nhat Minh
"""

from flask import Flask, render_template, flash, request, url_for, redirect, session, jsonify
import dbModel, mysql.connector
from mysql.connector import Error
from markupsafe import escape
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldjfasduosadfupoas'

# Define the strftime filter
def format_datetime(value, format='%Y-%m-%d'):
    return value.strftime(format)

# Register the filter with the app
app.jinja_env.filters['strftime'] = format_datetime

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
    hotels = hotel.getAll(100)

    email = session['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("booking/hotel.html", active_page=active_page, email=email, hotels=hotels)

@app.route('/booking/<int:hotel_id>')
def room_page(hotel_id):
    active_page = 'hotel'
    room = dbModel.Room()
    rooms = room.getAll(hotel_id, 500)

    hotel = dbModel.Hotel()
    hotels = hotel.getById(hotel_id)
    email = session['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("booking/room.html", active_page=active_page, email=email, rooms=rooms, hotels=hotels)

@app.route('/booking/<int:hotel_id>/confirm_booking/<int:room_id>', methods=['GET', 'POST'])
@login_required
def confirm_booking(hotel_id, room_id):
    room = dbModel.Room()
    room_details = room.getDetailById(room_id)
    print(room_details)
    booking_model = dbModel.Booking()
    user_model = dbModel.User()
    booking_date = datetime.now().date()  # Define booking_date outside the conditional block
    email = session.get('email', '')  # Retrieve email from session
    user_details = user_model.getByEmail(email)
    print(user_details)
    total_price = 0
    if request.method == 'POST':
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        # Calculate total price
        booking = {
            'users_id': user_details[0],
            'room_id': room_id,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'booking_date': datetime.now().date()
        }
        success, total_price = booking_model.calculate_total_price(booking)
        if success:
            booking['total_price'] = total_price
            booking_model.addNew(booking)
            flash('Book Completed!', category='success')
            return redirect(url_for('homepage',hotel_id=hotel_id, room_id=room_id, total_price=total_price))
        else:
            flash('Failed to book. Please try again', category='error')

    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("booking/confirm_booking.html", email = email, hotel_id=hotel_id, room_id = room_id, room_details = room_details, booking_date = booking_date, total_price = total_price, user_details = user_details)

@app.route('/booking/history')
@login_required
def booking_history():
    email = session['email'] if 'email' in session and session['email'] != '' else ''
    user_model = dbModel.User()
    user = user_model.getByEmail(email)
    users_id = user[0]
    print(users_id)
    booking_history = user_model.getBookingHistory(users_id)
    print(booking_history)
    return render_template("user/booking/booking_history.html", booking_history = booking_history)

@app.route('/booking/edit/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def change_booking(booking_id):
    booking_model = dbModel.Booking()
    booking_details = booking_model.getDetailById(booking_id)
    print(booking_details)
    if request.method == 'POST':
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        # Fetch other booking details from the existing booking
        room_id = booking_details[0]
        users_id = booking_details[1]
        booking_date = booking_details[6]
        # Construct the updated booking dictionary
        updated_booking = {
            'room_id': room_id,
            'users_id': users_id,
            'booking_date': booking_date,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date
        }
        print("Updated Booking:", updated_booking)  # Print updated booking details

        success, message = booking_model.updateBooking(booking_id, updated_booking)
        if success:
            flash('Changed Booking!',category='success')
            return redirect(url_for('booking_history'))  # Redirect to confirmation page
        else:
            flash(message, category='error')  # Flash error message if update fails
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("user/booking/edit.html", booking_details=booking_details, booking_id=booking_id, email = email)

@app.route('/booking/cancel/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def cancel_booking(booking_id):
    booking_model = dbModel.Booking()
    booking_details = booking_model.getDetailById(booking_id)
    if request.method == 'POST':
        confirmation = request.form.get('confirmation')
        if confirmation == 'yes':
            # Calculate cancellation charges
            success, cancellation_charges = booking_model.calculate_cancellation_charges(booking_id)
            if success:
                # Delete booking
                success, message = booking_model.delete_booking(booking_id)
                if success:
                    flash("Cancellation charges: ${:.2f}".format(cancellation_charges), category='error')
                    flash("Booking deleted successfully", category='success')
                    return redirect(url_for('booking_history'))
                else:
                    flash(message, category='error')
                    return redirect(url_for('booking_history'))  # Redirect if deletion fails
            else:
                flash("Error calculating cancellation charges", category='error')
                return redirect(url_for('booking_history', booking_id=booking_id))  # Redirect if calculation fails
        else:
            return redirect(url_for('booking_history', booking_id=booking_id))
    else:
        return render_template('user/booking/delete.html', booking_id=booking_id)

@app.route('/contact', methods=['POST', 'GET'])
def contact_page():
    active_page = 'contact'
    if request.method == 'POST':
        contact = dict()
        contact['name'] = request.form['name']
        contact['email'] = request.form['email']
        contact['message'] = request.form['message']
        contact_model = dbModel.Contact()
        if contact_model.addNew(contact):
            flash("Message sent!", category='success')
            return redirect(url_for('homepage'))
        else:
            flash("Error contacting", category='error')
            return redirect(url_for('contact_page'))
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
    session.pop('email', None)
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
        elif user['phoneNumber'] == '' or user_model.getByPhoneNumber(user['phoneNumber']):
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
                flash('Account created!', category='success')
                return redirect(url_for('login'))     

        # Flash error if the requirements are not met
        if user['email'] == '' or user_model.getByEmail(user['email']):
            flash('Email already exists', category='error')
        elif user['phoneNumber'] == '' or user_model.getByPhoneNumber(user['phoneNumber']):
            flash('Phone Number already exists', category='error')
        elif len(email) < 4:
            flash('Email must be at least 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be at least 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name must be at least 1 character.', category='error')
        elif not phoneNumber.replace('+','').isdigit():
            flash('Phone number only contain numbers.', category='error')
        elif len(phoneNumber) < 9:
            flash('Phone number must be at least 9 characters.', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
        elif password != password1:
            flash('Password don\'t match.', category='error')
        elif captcha_input != session['captcha']:
            flash('CAPTCHA incorrect. Please try again.', category='error')
        elif not agree_terms:
            flash('Please agree to the terms of service.', category='error')


    session['captcha'] = dbModel.generate_captcha()     # Generate CAPTCHA
    return render_template("user/auth/sign_up.html", captcha=session['captcha'])

@app.route('/check-email', methods=['POST'])
def check_email():
    email = request.json['email']
    user_model = dbModel.User()
    if user_model.check_email_exists(email):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
    
@app.route('/check-phone-number', methods=['POST'])
def check_phone_number():
    phoneNumber = request.json['phoneNumber']
    user_model = dbModel.User()
    if user_model.check_phone_number_exists(phoneNumber):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@app.route('/terms_of_services')
def terms_of_services():
    return render_template("user/auth/ToS.html")

@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    email = session ['email'] if 'email' in session and session['email'] != '' else ''

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            flash('Passwords do not match. Please try again.', category='error')
            return redirect(url_for('reset_password'))
        elif len(new_password) < 8:
            return redirect(url_for('reset_password'))
        
        if new_password != '':
            user_model = dbModel.User()
            if user_model.reset_password(new_password, email):
                flash('Password changed!', category='success')
                return redirect(url_for('login'))     
        
    return render_template("user/auth/reset_password.html", email = email)


######      ADMIN       #####
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    customer = dbModel.User()
    users = customer.getAll(5)
    hotel_model = dbModel.Hotel()
    room_model = dbModel.Room()
    # print(users)
    # Get current week, month, year
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_week = datetime.now().isocalendar()[1]
    # Query the database to get monthly sales
    booking_model = dbModel.Booking()
    # Total Booking
    total_booking = booking_model.countTotalBookings()
    total_bookings_month = booking_model.countTotalBookingsForMonth(current_month, current_year)
    total_bookings_week = booking_model.countTotalBookingsForWeek(current_year, current_week)
    # Monthly Sales
    monthly_sales = booking_model.get_monthly_sales(current_month, current_year)
    # Top Customers
    top_customers = booking_model.get_top_customers(5)
    # Count available rooms
    available_rooms = room_model.countAvailableRooms()
    # Count booked rooms
    booked_rooms = room_model.countBookedRooms()
    # Count booked rooms by room type
    booked_rooms_by_type = room_model.countBookedRoomsByType()
    # Count hotel with least room booked and most room booked
    lowest_hotel, highest_hotel = hotel_model.get_lowest_and_highest_booked_hotels()
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/dashboard.html", email=email, users=users, monthly_sales=monthly_sales, 
                           top_customers=top_customers, total_booking=total_booking, total_bookings_month=total_bookings_month, 
                           total_bookings_week=total_bookings_week, available_rooms=available_rooms, booked_rooms=booked_rooms,
                           booked_rooms_by_type=booked_rooms_by_type, lowest_hotel=lowest_hotel, highest_hotel=highest_hotel)

@app.route('/admin/booking/all_bookings')
@login_required
def all_bookings():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    booking_model = dbModel.Booking()
    all_booking = booking_model.getAll(500)
    total_booking = booking_model.countTotalBookings()
    print(all_booking)
    return render_template("admin/booking/all_bookings.html", email = email, all_booking = all_booking, total_booking=total_booking)

@app.route('/admin/booking/edit/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_booking(booking_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    booking_model = dbModel.Booking()
    booking_details = booking_model.getDetailById(booking_id)
    if request.method == 'POST':
        booking = dict()
        booking['booking_ID'] = booking_id
        booking['check_in_date'] = request.form['check_in_date']
        booking['check_out_date'] = request.form['check_out_date']
        booking['total_price'] = request.form['total_price']
        if booking_model.updateBooking(booking):
            flash('Updated Booking!', category='success')
            return redirect(url_for('all_bookings'))
        else:
            flash('Failed updating booking', category='error')
            return redirect(url_for('admin_edit_booking'))
    return render_template("admin/booking/edit.html", booking_details = booking_details)

@app.route('/admin/booking/delete/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def admin_delete_booking(booking_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    booking_model = dbModel.Booking()
    booking_details = booking_model.getDetailById(booking_id)
    if request.method == 'POST':
        confirmation = request.form.get('confirmation')
        if confirmation == 'yes':
            booking_model.delete_booking(booking_id)
            flash('Deleted booking successfully', category='success')
            return redirect(url_for('all_bookings'))
        else:
            flash('Error deleting booking', category='error')
            return redirect(url_for('all_bookings'))
    return render_template("admin/booking/delete.html")

@app.route('/admin/all_hotels')
@login_required
def all_hotels():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    hotel = dbModel.Hotel()
    hotels = hotel.getAll(100)
    # print(hotels)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/hotel/hotel_list.html", email = email, hotels = hotels)

@app.route('/admin/add_hotel', methods=['GET', 'POST'])
@login_required
def add_hotel():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    hotel_model = dbModel.Hotel()
    if request.method == 'POST':
        capacity = int(request.form.get('capacity'))
        hotel = dict()
        hotel['city'] = request.form['city']
        hotel['hotel_name'] = request.form['hotel_name']
        hotel['email'] = request.form['email']
        hotel['phone'] = request.form['phone']
        hotel['capacity'] = request.form['capacity']

        if len(hotel['city']) < 1:
            flash('City name must be at least 1 character', category='error')
        elif len(hotel['hotel_name']) < 1:
            flash('Hotel name must be at least 1 character', category='error')
        elif len(hotel['email']) < 3:
            flash('Hotel email must be at least 3 characters', category='error')
        elif len(hotel['phone']) < 9:
            flash('Hotel phone number must be at least 9 characters.', category='error')
        elif capacity < 1:
            flash('Hotel must have at least 1 room', category='error')
        if hotel_model.addNew(hotel):
            flash('Added hotel', category='success')
            return redirect(url_for('all_hotels'))
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/hotel/add_hotel.html", email = email)

@app.route('/admin/hotel_edit/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def edit_hotel(hotel_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    hotel_model = dbModel.Hotel()
    hotel_details = hotel_model.getById(hotel_id)

    if request.method == 'POST':
        hotel = {
            'hotel_id': hotel_id,
            'city': request.form['city'],
            'hotel_name': request.form['hotel_name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'capacity': request.form['capacity']
        }

        if hotel_model.update(hotel):
            flash('Update hotel successfully', category='success')
            print("Redirecting to all_hotels route")
            return redirect(url_for('all_hotels'))
        else:
            flash("Error updating hotel", category='error')
            return redirect(url_for('edit_hotel', hotel_id=hotel_id))

    email = session['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/hotel/edit_hotel.html", email=email, hotel_id=hotel_id, hotel_details=hotel_details)


@app.route('/admin/delete_hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def delete_hotel(hotel_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    hotel_model = dbModel.Hotel()
    hotel_details = hotel_model.getDetailById(hotel_id)
    if request.method == 'POST':
        confirmation = request.form.get('confirmation')
        if confirmation == 'yes':
            hotel_model.delete(hotel_id)
            flash('Deleted hotel successfully', category='success')
            return redirect(url_for('all_hotels'))
        else:
            flash('Deletion cancelled', category='error')
            return redirect(url_for('all_hotels'))
    return render_template("admin/hotel/delete_hotel.html")

@app.route('/admin/<int:hotel_id>/room_list')
@login_required
def room_list(hotel_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    room = dbModel.Room()
    rooms = room.getAll(hotel_id, 500)

    hotel = dbModel.Hotel()
    hotels = hotel.getById(hotel_id)

    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/room/room_list.html", email=email, rooms=rooms, hotels=hotels)

@app.route('/admin/<int:hotel_id>/add_room', methods=['GET', 'POST'])
@login_required
def add_room(hotel_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    room_model = dbModel.Room()
    rooms = room_model.getAll(hotel_id, 500)
    hotel = dbModel.Hotel()
    hotels = hotel.getById(hotel_id)
    status = 'Available'
    if request.method == 'POST':
        room = dict()
        room['hotel_id'] = hotel_id
        room['room_type'] = request.form['room_type']
        room['features'] = request.form['features']
        room['peak_season_price'] = request.form['peak_season_price']
        room['off_peak_price'] = request.form['off_peak_price']
        room['status'] = status
        if room_model.addNew(room):
            flash('Added new room!', category='success')
            return redirect(url_for('room_list', hotel_id=hotel_id))
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/room/add_room.html", email = email, rooms=rooms, hotels=hotels, status = status)

@app.route('/admin/<int:hotel_id>/edit_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(hotel_id, room_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    room_model = dbModel.Room()
    room_details = room_model.getDetailById(room_id)
    print(room_details)
    if request.method == 'POST':
        room = dict()
        room['room_id'] = room_id
        room['hotel_id'] = hotel_id
        room['room_type'] = request.form['room_type']
        room['features'] = request.form['features']
        room['peak_season_price'] = request.form['peak_season_price']
        room['off_peak_price'] = request.form['off_peak_price']
        room['status'] = request.form['status']

        if room_model.update(room):
            flash("Update room successfully", category='success')
            print("Redirecting to room_lists route")
            return redirect(url_for('room_list', hotel_id = hotel_id))
        else:
            flash("Error updating hotel", category='error')
            return redirect(url_for('edit_room', hotel_id = hotel_id, room_id = room_id))
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template("admin/room/edit_room.html", email=email, hotel_id=hotel_id, room_id=room_id, room_details = room_details)

@app.route('/admin/<int:hotel_id>/delete_room/<int:room_id>', methods=['GET','POST'])
@login_required
def delete_room(hotel_id, room_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    room_model = dbModel.Room()
    room_details = room_model.getDetailById(room_id)
    print(room_details)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    if request.method == 'POST':
        confirmation = request.form.get('confirmation')
        if confirmation == 'yes':
            room_model.delete(room_id)
            flash('Room deleted successfully', category='success')
            return redirect(url_for('room_list', hotel_id = hotel_id))
        else:
            flash('Deletion cancelled', category='error')
            return redirect(url_for('room_list', hotel_id = hotel_id))
    return render_template("admin/room/delete_room.html", email=email, hotel_id=hotel_id, room_id=room_id)

@app.route('/admin/customers/list')
@login_required
def customers_list():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    customer = dbModel.User()
    users = customer.getAll(100)
    # Total Customers
    total_customers = customer.count_total_users()
    # print(users)
    email = session ['email'] if 'email' in session and session['email'] != '' else ''
    return render_template('admin/customers/list.html', email = email, users = users, total_customers = total_customers)

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

@app.route('/admin/customers/<users_id>/activities')
@login_required
def customers_activities(users_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    email = session['email'] if 'email' in session and session['email'] != '' else ''
    user_model = dbModel.User()
    user = user_model.getById(users_id)
    print(users_id)
    booking_history = user_model.getBookingHistory(users_id)
    print(booking_history)
    return render_template("admin/customers/activities.html", user=user, booking_history=booking_history)

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
            flash('Update user successfully', category='success')
            return redirect(url_for('customers_details', users_id = user['users_id']))
        else:
            print('Error')
            print(user)
            flash('Error updating user', category='error')
            return redirect(url_for('customers_edit', users_id = user['users_id']))
    else:
        users = customer.getById(users_id)
    return render_template('admin/customers/edit.html', user = users, email = email)

@app.route('/admin/customers/delete/<users_id>', methods=['GET', 'POST'])
@login_required
def delete_customer(users_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    user_model = dbModel.User()
    user_details = user_model.getDetailById(users_id)
    if request.method == 'POST':
        confirmation = request.form.get('confirmation')
        if confirmation == 'yes':
            user_model.delete(users_id)
            flash('Deleted customer successfully', category='success')
            return redirect(url_for('customers_list'))
        else:
            flash('Deletion cancelled', category='error')
            return redirect(url_for('customers_list'))
    return render_template("admin/customers/delete.html")


@app.route('/admin/monthly_sales')
@login_required
def monthly_sales_report():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Query the database to get monthly sales
    booking_model = dbModel.Booking()
    monthly_sales = booking_model.get_monthly_sales(current_month, current_year)

    # Render the template with the monthly sales data
    return render_template('admin/reports/monthly_sales.html', month=current_month, year=current_year, monthly_sales=monthly_sales)

@app.route('/admin/sales_for_each_hotel')
@login_required
def sales_for_each_hotel():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Query the database to get monthly sales for each hotel
    booking_model = dbModel.Booking()
    monthly_sales_by_hotel = booking_model.get_monthly_sales_by_hotel(current_month, current_year)
    return render_template("admin/reports/sales_for_each_hotel.html", monthly_sales_by_hotel=monthly_sales_by_hotel)

@app.route('/admin/top_customers')
@login_required
def top_customers():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))
    
    # Call the method to get the top customers from the database model
    booking_model = dbModel.Booking()
    top_customers = booking_model.get_top_customers(10)

    # Render the template with the top customers data
    return render_template('admin/customers/top_customers.html', top_customers=top_customers)

@app.route('/admin/contacts', methods=['GET'])
@login_required
def admin_all_contacts():
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    contact_model = dbModel.Contact()
    contacts = contact_model.getAll(100)
    return render_template('admin/contact.html', contacts=contacts)

@app.route('/admin/contact/delete/<int:contact_id>', methods=['POST'])
@login_required
def admin_delete_contact(contact_id):
    if session['usertype'] != 'admin':
        flash('Unauthorized Access', category='error')
        return redirect(url_for('homepage'))

    contact_model = dbModel.Contact()
    contact_model.delete(contact_id)
    flash('Contact deleted successfully', category='success')
    return redirect(url_for('admin_all_contacts'))


# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)