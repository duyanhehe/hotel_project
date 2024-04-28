import mysql.connector, dbfunc
from mysql.connector import errorcode, Error
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta

connect = dbfunc.getConnection()

# Function to generate a random CAPTCHA string
def generate_captcha():
    captcha_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    captcha = ''.join(random.choices(captcha_chars, k=6))
    return captcha

class Model:
    def __init__(self):
        self.conn = connect
        self.tbName = ''
        if self.conn != None:
            if self.conn.is_connected():
                self.dbcursor = self.conn.cursor()
        else:
            print('DBfunc error')

    def getAll(self, limit = 10):
        try:
            self.dbcursor.execute('select * from '+ self.tbName + ' limit '+ str(limit))
            my_result = self.dbcursor.fetchall()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    

class User(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'users'
    
    def addNew(self, user):
        try:
            self.dbcursor.execute('insert into '+ self.tbName + 
                                ' (email, firstName, lastName, phoneNumber, password_hash, usertype) values (%s, %s, %s, %s, %s, %s)',
                                    (user['email'], user['firstName'], user['lastName'], user['phoneNumber'], generate_password_hash(user['password']), user['usertype']))
            my_result = self.conn.commit()
        except Error as e:
            print(e)
            return False   
        else:    
            if self.dbcursor.rowcount == 0:
                return False            
        return True
    
    def getById(self, users_id):
        try:
            self.dbcursor.execute('select * from '+ self.tbName + ' where users_id = {}'.format(users_id))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    

    def getDetailById(self, users_id):
        try:
            self.dbcursor.execute('SELECT users.*, booking.*, room.room_id, room.room_type FROM users \
                                   LEFT JOIN booking ON users.users_id = booking.users_id \
                                   LEFT JOIN room ON booking.room_id = room.room_id \
                                   WHERE users.users_id = {}'.format(users_id))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result
    
    def getByEmail(self, email):
        try:
            self.dbcursor.execute('select * from '+ self.tbName + ' where email = %s',(email,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    
    def getByPhoneNumber(self, phoneNumber):
        try:
            self.dbcursor.execute('SELECT * FROM '+ self.tbName + ' WHERE phoneNumber = %s',(phoneNumber,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    
    def getBookingHistory(self, users_id):
        try:
            self.dbcursor.execute('SELECT * FROM booking \
                                  LEFT JOIN room ON booking.room_id = room.room_id \
                                  WHERE users_id = {}'.format(users_id))
            my_result = self.dbcursor.fetchall()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    
    def checkLogin(self, email, password):
        user = self.getByEmail(email)
        if user:
            # print(user)
            if check_password_hash(user[5], password):
                return True
        return False
    
    def check_email_exists(self, email):
        try:
            self.dbcursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            my_result = self.dbcursor.fetchone()[0]
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    
    def check_phone_number_exists(self, phoneNumber):
        try:
            self.dbcursor.execute("SELECT COUNT(*) FROM users WHERE phoneNumber = %s", (phoneNumber,))
            my_result = self.dbcursor.fetchone()[0]
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    
    def update_user(self, user):
        try:
            self.dbcursor.execute('update ' + self.tbName +
                                  ' set email = %s, firstName = %s, lastName = %s, phoneNumber = %s, password_hash = %s, usertype = %s \
                                    where users_id = %s',
                                    (user['email'], user['firstName'], user['lastName'], user['phoneNumber'], generate_password_hash(user['password']), user['usertype'], user['users_id']))
            my_result = self.conn.commit()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                return False
        
        return True  

    def delete(self, users_id):
        try:
            delete_query = "DELETE FROM {} WHERE users_id = %s".format(self.tbName)
            self.dbcursor.execute(delete_query, (users_id,))
            self.conn.commit()
        except Error as e:
            print(e)

    def reset_password(self, password, email):
        try:
            self.dbcursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (generate_password_hash(password), email))
            my_result = self.conn.commit()
            return True
        except Error as e:
            print(e)
            return False

class Hotel(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'hotel'
    
    def getById(self, hotel_id):
        try:
            self.dbcursor.execute('SELECT * FROM ' + self.tbName + ' WHERE hotel_id = %s', (hotel_id,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()      
        return my_result

    def getDetailById(self, hotel_id):
        try:
            self.dbcursor.execute('''
                SELECT hotel.*, room.room_id, room.room_type, room.features, room.peak_season_price, room.off_peak_price, room.status
                FROM hotel
                LEFT JOIN room ON hotel.hotel_id = room.hotel_id
                WHERE hotel.hotel_id = %s
            ''', (hotel_id,))
            my_result = self.dbcursor.fetchall()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result

    def addNew(self, hotel):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (city, hotel_name, email, phone, capacity) VALUES (%s, %s, %s, %s, %d)',
                                  (hotel['city'], hotel['hotel_name'], hotel['email'], hotel['phone'], hotel['capacity']))
            my_result = self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def delete(self, hotel_id):
        try:
            delete_query = "DELETE FROM {} WHERE hotel_id = %s".format(self.tbName)
            self.dbcursor.execute(delete_query, (hotel_id,))
            self.conn.commit()
        except Error as e:
            print(e)

    def delete_room(self, room_id):
        try:
            delete_query = "DELETE FROM room WHERE room_id = %s"
            self.dbcursor.execute(delete_query, (room_id,))
            self.conn.commit()
        except Error as e:
            print(e)
            
    
class Room(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'room'

    def getAll(self, hotel_id, limit = 10):
        try:
            sql = "SELECT * FROM " + self.tbName + " WHERE hotel_id = %s LIMIT %s"
            self.dbcursor.execute(sql, (hotel_id, limit))
            my_result = self.dbcursor.fetchall()
        except Error as e:
            print(e)
            my_result = ()
        else:    
            if self.dbcursor.rowcount == 0:
                my_result = ()            
        return my_result
    

    def getById(self, room_id):
        try:
            self.dbcursor.execute('SELECT * FROM ' + self.tbName + ' WHERE room_id = %s', (room_id,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result
    
    def getDetailById(self, room_id):
        try:
            self.dbcursor.execute('''
                SELECT room.*, hotel.city, hotel.hotel_name, hotel.email, hotel.phone
                FROM room
                INNER JOIN hotel ON room.hotel_id = hotel.hotel_id
                WHERE room.room_id = %s
            ''', (room_id,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result

    def addNew(self, room):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + ' (hotel_id, room_type, features, peak_season_price, off_peak_price, status) \
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                                  (room['hotel_id'], room['room_type'], room['features'], room['peak_season_price'], room['off_peak_price'], room['status']))
            my_result = self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def updateRoomStatus(self, room_id, status):
        try:
            self.dbcursor.execute('UPDATE ' + self.tbName + ' SET status = %s WHERE room_id = %s', (status, room_id))
            self.conn.commit()
        except Error as e:
            print(e)

class Booking(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'booking'

    def calculate_total_price(self, booking):
        # Extract relevant booking information
        booking['booking_date'] = datetime.now().date()
        check_in_date_str = booking['check_in_date']
        check_out_date_str = booking['check_out_date']
        room_id = booking['room_id']
        
        # Fetch peak_season_price and off_peak_price from room table based on room_id
        room_instance = Room()
        room_details = room_instance.getDetailById(room_id)
        if room_details:
            peak_season_price = room_details[4]
            off_peak_price = room_details[5]
        else:
            # If room details are not available, default to base_price
            peak_season_price = 0
            off_peak_price = 0

        check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d')
        # Check if check in date is in peak season (April - August, November - December)
        if check_in_date.month in [4, 5, 6, 7, 8, 11, 12]:
            total_price = peak_season_price
        else:
            total_price = off_peak_price

        # Calc the difference between check-in date and booking date
        booking_date = booking['booking_date']
        days_difference = (check_in_date - datetime.combine(booking_date, datetime.min.time())).days

        # Determine discount % based on days difference
        if days_difference > 90:
            return False, "You can not book over 3 months in advance"
        elif days_difference >= 80 and days_difference <= 90:
            discount_percentage = 0.3   # 30% discount
        elif days_difference >= 60 and days_difference < 80:
            discount_percentage = 0.2   # 20% discount
        elif days_difference >= 45 and days_difference < 60:
            discount_percentage = 0.1   # 10% discount
        else:
            discount_percentage = 0.0   # No discount
        # Calc total price after discount
        total_price -= total_price * discount_percentage

        # Calculate total price multiplied by the number of days staying
        if 'check_out_date' in booking:
            check_out_date = datetime.strptime(booking['check_out_date'], '%Y-%m-%d')
            days_staying = (check_out_date - check_in_date).days
            total_price *= days_staying
        else:
            days_staying = 0

        return True, total_price

    def updateBooking(self, booking_id, new_booking):
        try:
            original_booking = self.getDetailById(booking_id)
            if not original_booking:
                return False, "Booking not found"
            
            # Extract original booking details
            original_check_in_date = original_booking[3]
            original_check_out_date = original_booking[4]
            original_booking_date = original_booking[6]
            original_total_price = original_booking[5]

            # Extract updated booking details
            updated_check_in_date = new_booking.get('check_in_date', original_check_in_date)
            updated_check_out_date = new_booking.get('check_out_date', original_check_out_date)

            # Check if check_in_date or check_out_date is changed
            if updated_check_in_date != original_check_in_date or updated_check_out_date != original_check_out_date:
                # Recalculate total price if dates are changed
                new_booking['check_in_date'] = updated_check_in_date
                new_booking['check_out_date'] = updated_check_out_date
                success, new_total_price = self.calculate_total_price(new_booking)
                if not success:
                    return False, new_total_price
            else:
                # Keep the original total price if dates remain unchanged
                new_total_price = original_total_price
            
            print("Updated Booking Details:", new_booking)  # Print updated booking details for troubleshooting

            # Update the booking in the database
            self.dbcursor.execute('UPDATE ' + self.tbName + ' SET check_in_date = %s, check_out_date = %s, total_price = %s WHERE booking_ID = %s',
                                  (updated_check_in_date, updated_check_out_date, new_total_price, booking_id))
            self.conn.commit()

            return True, "Booking updated successfully"
        except Exception as e:
            print(e)
            return False, "Error occurred during booking update"

    def addNew(self, booking):
        # Update room status to "unavailable"
        room_instance = Room()
        room_instance.updateRoomStatus(booking['room_id'], 'Unavailable')
        try:
            success, total_price = self.calculate_total_price(booking)
            if not success:
                return False, total_price
            
            total_price = str(total_price)

            #  Insert into database
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (users_id, room_id, check_in_date, check_out_date, total_price, booking_date) \
                                      VALUES (%s, %s, %s, %s, %s, %s)',
                                  (booking['users_id'], booking['room_id'] ,booking['check_in_date'], booking['check_out_date'], total_price, booking['booking_date']))
            self.conn.commit()

            # Schedule task to update room status back to "available" after check_out_date
            check_out_date = datetime.strptime(booking['check_out_date'], '%Y-%m-%d').date()
            schedule_task = datetime.combine(check_out_date, datetime.min.time()) + timedelta(days=1)
            schedule_task = schedule_task.strftime('%Y-%m-%d %H:%M:%S')
            self.dbcursor.execute(f"CREATE EVENT IF NOT EXISTS Room_Availability_{booking['room_id']} \
                                    ON SCHEDULE AT '{schedule_task}' \
                                    DO UPDATE {room_instance.tbName} SET status = 'Available' WHERE room_id = {booking['room_id']};")
            self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def getById(self, booking_ID):
        try:
            self.dbcursor.execute('SELECT * FROM ' + self.tbName + ' WHERE booking_ID = %s', (booking_ID,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result
    
    def getDetailById(self, booking_ID):
        try:
            query = '''
                    SELECT booking.*, room.room_type
                    FROM booking
                    LEFT JOIN room ON booking.room_id = room.room_id
                    WHERE booking.booking_ID = %s'''
            self.dbcursor.execute(query, (booking_ID,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result

    def getDetailByRoomId(self, room_id):
        try:
            query = '''
                SELECT booking.booking_ID, booking.users_id, booking.room_id, booking.check_in_date, booking.check_out_date, 
                    booking.total_price, booking.booking_date,
                    users.email, users.firstName, users.lastName, users.phoneNumber,
                    room.room_type, room.features, room.peak_season_price, room.off_peak_price
                FROM booking
                LEFT JOIN users ON booking.users_id = users.users_id
                LEFT JOIN room ON booking.room_id = room.room_id
                WHERE booking.room_id = %s
            '''
            self.dbcursor.execute(query, (room_id,))
            my_result = self.dbcursor.fetchall()
        except Error as e:
            print("Error retrieving booking details:", e)
            my_result = ()
        else:
            if not my_result:
                print("No booking details found.")
        return my_result
    
    def getAll(self, limit=10):
        try:
            sql = '''
                SELECT 
                    booking.booking_ID, 
                    booking.users_id, 
                    booking.room_id, 
                    booking.check_in_date, 
                    booking.check_out_date, 
                    booking.total_price, 
                    booking.booking_date,
                    users.email, 
                    users.firstName, 
                    users.lastName, 
                    users.phoneNumber,
                    room.room_type, 
                    room.features, 
                    room.peak_season_price, 
                    room.off_peak_price
                FROM 
                    booking
                JOIN 
                    users ON booking.users_id = users.users_id
                JOIN 
                    room ON booking.room_id = room.room_id
                LIMIT %s
            '''

            self.dbcursor.execute(sql, (limit,))
            my_result = self.dbcursor.fetchall()
        except Error as e:
            print("Error retrieving booking details:", e)
            my_result = ()
        else:
            if not my_result:
                print("No booking details found.")
        return my_result
