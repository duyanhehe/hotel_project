import mysql.connector, dbfunc
from mysql.connector import errorcode, Error
from werkzeug.security import generate_password_hash, check_password_hash
import random

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
    
    def checkLogin(self, email, password):
        user = self.getByEmail(email)
        if user:
            # print(user)
            if check_password_hash(user[5], password):
                return True
        return False
    
    def reset_password(self, email, password):
        hashed_password = generate_password_hash(password)
        try:
            self.dbcursor.execute('UPDATE users SET password = %s WHERE email = %s', (hashed_password, email))
            self.conn.commit()
            return True
        except Error as e:
            print(e)
            return False

    def verify_password(self, email, password):
        hashed_password = self.get_hashed_password(email)
        if hashed_password:
            return check_password_hash(hashed_password, password)
        return False

class Hotels(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'hotels'
    
    def addNew(self, hotel):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (address, email, phone, stars, check_in_time, check_out_time) VALUES (%s, %s, %s, %s, %s, %s)',
                                  (hotel['address'], hotel['email'], hotel['phone'], hotel['stars'], hotel['check_in_time'], hotel['check_out_time']))
            my_result = self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True
    
    def getByHotelId(self, hotel_id):
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


class Room(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'rooms'

    def addNew(self, room):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (hotel_id, room_type_id, status) VALUES (%s, %s, %s)',
                                  (room['hotel_id'], room['room_type_id'], room['status']))
            self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def getByRoomNumber(self, room_number):
        try:
            self.dbcursor.execute('SELECT * FROM ' + self.tbName + ' WHERE room_number = %s', (room_number,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result


class RoomTypes(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'room_types'

    def addNew(self, room_type):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (name, description, price_per_night, capacity) VALUES (%s, %s, %s, %s)',
                                  (room_type['name'], room_type['description'], room_type['price_per_night'], room_type['capacity']))
            self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def getById(self, room_type_id):
        try:
            self.dbcursor.execute('SELECT * FROM ' + self.tbName + ' WHERE room_type_id = %s', (room_type_id,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result


class Bookings(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'bookings'

    def addNew(self, booking):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (guest_ID, room_number, check_in_date, check_out_date, total_price) VALUES (%s, %s, %s, %s, %s)',
                                  (booking['guest_ID'], booking['room_number'], booking['check_in_date'], booking['check_out_date'], booking['total_price']))
            self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def getByBookingId(self, booking_ID):
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


class Payment(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'payment'

    def addNew(self, payment):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (booking_ID, amount, payment_date, payment_method) VALUES (%s, %s, %s, %s)',
                                  (payment['booking_ID'], payment['amount'], payment['payment_date'], payment['payment_method']))
            self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True

    def getById(self, payment_ID):
        try:
            self.dbcursor.execute('SELECT * FROM ' + self.tbName + ' WHERE payment_ID = %s', (payment_ID,))
            my_result = self.dbcursor.fetchone()
        except Error as e:
            print(e)
            my_result = ()
        else:
            if self.dbcursor.rowcount == 0:
                my_result = ()
        return my_result