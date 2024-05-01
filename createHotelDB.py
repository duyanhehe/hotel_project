"""
TEAM MEMBERS
- Tran Duy Anh
- Nguyen Quang Manh
- Bui Vu Nhat Minh
"""

import mysql.connector
from mysql.connector import Error, errorcode
from werkzeug.security import generate_password_hash
from dbfunc import hostname, username, passwd
import random
import string

def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)
    else:  #will execute if there is no exception raised in try block
        if(conn.is_connected):
            return conn
        else:
            conn.close()

# Function to generate a random string of fixed length
def random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

# create tables and insert mock data
def create_tables():
    try:
        connection = getConnection()
        cursor = connection.cursor()

        #################       CREATE DATABASE     #################
        # Drop database if exists
        cursor.execute("DROP DATABASE IF EXISTS hotel_db")

        # Create database
        cursor.execute("CREATE DATABASE hotel_db")

        # Use hotel_db
        cursor.execute("USE hotel_db")

        #################       CREATE TABLE        #################
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            users_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(120) NOT NULL UNIQUE,
            firstName VARCHAR(50) NOT NULL,
            lastName VARCHAR(50) NOT NULL,
            phoneNumber VARCHAR(15) NOT NULL UNIQUE,
            password_hash VARCHAR(255),
            usertype VARCHAR(8) DEFAULT 'standard'
        )""")

        # Create hotel table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel (
            hotel_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
            city VARCHAR(255) NOT NULL,
            hotel_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(15) NOT NULL,
            capacity INT NOT NULL
        )""")

        # Create room table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS room (
            room_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
            hotel_id INT NOT NULL, 
            room_type VARCHAR(50) NOT NULL,
            features VARCHAR(255) NOT NULL,
            peak_season_price FLOAT NOT NULL, 
            off_peak_price FLOAT NOT NULL, 
            status VARCHAR(20), 
            FOREIGN KEY (hotel_id) REFERENCES hotel(hotel_id) ON DELETE CASCADE
        )""")

        # Create booking table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            booking_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
            users_id INT NOT NULL,
            room_id INT NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            total_price FLOAT NOT NULL,
            booking_date DATE NOT NULL,
            FOREIGN KEY (users_id) REFERENCES users(users_id) ON DELETE CASCADE,
            FOREIGN KEY (room_id) REFERENCES room(room_id) ON DELETE CASCADE
        )""")

        # Create trigger to update room status to "Booked" when a booking is inserted
        cursor.execute("""
        CREATE TRIGGER update_room_status
        AFTER INSERT ON booking
        FOR EACH ROW
        BEGIN
            UPDATE room
            SET status = 'Booked'
            WHERE room_id = NEW.room_id;
        END;
        """)

        # Create contact table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact (
            contact_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            message TEXT NOT NULL
        )""")

        #################       INSERT MOCK DATA        #################
        # Insert Admin User
        admin_password = 'adminpassword'
        password = generate_password_hash(admin_password)
        cursor.execute("""INSERT INTO users (email, firstName, lastName, phoneNumber, password_hash, usertype)
                        VALUES ('admin@gmail.com', 'Ad', 'Min', '1231684968', %s, 'admin')""", (password,))
        
        # Insert users
        for i in range(10):
            email = f'user{i+1}@gmail.com'
            firstName = random_string(5)
            lastName = random_string(5)
            phoneNumber = ''.join(random.choices(string.digits, k=9))
            password_hash = generate_password_hash('password')
            cursor.execute("""INSERT INTO users (email, firstName, lastName, phoneNumber, password_hash, usertype)
                            VALUES (%s, %s, %s, %s, %s, 'standard')""",
                        (email, firstName, lastName, phoneNumber, password_hash))

        # Insert hotels
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Aberdeen', 'Aberdeen Hotel', 'aberdeenHotel@gmail.com', '999999999', 40)""")
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Belfast', 'Belfast Hotel', 'belfastHotel@gmail.com', '888888888', 30)""")
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Birmingham', 'Birmingham Hotel', 'birminghamHotel@gmail.com', '777777777', 60)""")
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Bristol', 'Bristol Hotel', 'bristolHotel@gmail.com', '666666666', 50)""")
        
        ## Insert rooms into aberdeen hotel
        # Standard Rooms
        for i in range(0, 12):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (1, 'Standard', 'Wifi, TV', 60.00, 40.00, 'Available')""")
        # Double Rooms
        for i in range(0, 20):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (1, 'Double', 'Wifi, TV, mini-bar', 72.00, 50.40, 'Available')""")
        # Family Rooms 
        for i in range(0, 8):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (1, 'Family', 'Wifi, TV, mini-bar, breakfast', 90.00, 60.00, 'Available')""")
            
        ## Insert rooms into belfast hotel
        # Standard Rooms
        for i in range(0, 9):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (2, 'Standard', 'Wifi, TV, AC', 50.00, 30.00, 'Available')""")
        # Double Rooms
        for i in range(0, 15):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (2, 'Double', 'Wifi, TV, mini-bar, AC', 60.00, 36.00, 'Available')""")
        # Family Rooms 
        for i in range(0, 6):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (2, 'Family', 'Wifi, TV, AC, mini-bar, breakfast', 75.00, 45.00, 'Available')""")
            
        ## Insert rooms into birmingham hotel
        # Standard Rooms
        for i in range(0, 18):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (3, 'Standard', 'Wifi, TV, AC', 65.00, 45.00, 'Available')""")
        # Double Rooms
        for i in range(0, 30):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (3, 'Double', 'Wifi, TV, mini-bar, AC', 78.00, 54.00, 'Available')""")
        # Family Rooms 
        for i in range(0, 12):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (3, 'Family', 'Wifi, TV, AC, mini-bar, breakfast', 97.50, 67.50, 'Available')""")
            
        ## Insert rooms into bristol hotel
        # Standard Rooms
        for i in range(0, 15):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (4, 'Standard', 'Wifi, TV, AC', 59.99, 39.99, 'Available')""")
        # Double Rooms
        for i in range(0, 25):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (4, 'Double', 'Wifi, TV, mini-bar, AC', 90.00, 70.00, 'Available')""")
        # Family Rooms 
        for i in range(0, 10):
            cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                        VALUES (4, 'Family', 'Wifi, TV, AC, mini-bar, breakfast', 200.00, 120.00, 'Available')""")

        # Insert into booking
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (2, 4, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (2, 5, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (2, 6, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (3, 7, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (4, 8, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (5, 9, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (6, 10, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (7, 11, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (8, 12, '2024-06-25', '2024-06-28', 60.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (9, 13, '2024-06-25', '2024-06-28', 72.00, '2024-05-21')""")
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (10, 14, '2024-06-25', '2024-06-28', 72.00, '2024-05-21')""")

        connection.commit()
        connection.close()

    except mysql.connector.Error as err:
        print("Error:", err)


if __name__ == "__main__":
    create_tables()