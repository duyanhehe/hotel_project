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
    
    # TODO: getDetailById
    def getDetailById(self, users_id):
        pass
    
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

class Room(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'room'

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
    
    #TODO: Get detail by id
    def getDetailById(self, room_id):
        pass

    def addNew(self, room):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + ' (hotel_id, room_type, features, base_price, peak_season_price, off_peak_price, status) \
                                  VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                                  (room['hotel_id'], room['room_type'], room['features'], room['base_price'], room['base_price'], room['peak_season_price'], room['off_peak_price'], room['status']))
            my_result = self.conn.commit()
        except Error as e:
            print(e)
            return False
        else:
            if self.dbcursor.rowcount == 0:
                return False
        return True


class Booking(Model):
    def __init__(self):
        super().__init__()
        self.tbName = 'booking'

    def addNew(self, booking):
        try:
            self.dbcursor.execute('INSERT INTO ' + self.tbName + 
                                  ' (users_id, room_id, check_in_date, check_out_date, total_price, booking_date) \
                                      VALUES (%s, %s, %s, %s, %s, %s)',
                                  (booking['users_id'], booking['room_id'] ,booking['check_in_date'], booking['check_out_date'], booking['total_price'], booking['booking_date']))
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
