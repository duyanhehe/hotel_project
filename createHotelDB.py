import mysql.connector
from mysql.connector import Error, errorcode
from werkzeug.security import generate_password_hash
from dbfunc import hostname, username, passwd
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

from werkzeug.security import generate_password_hash

def create_tables():
    try:
        connection = getConnection()
        cursor = connection.cursor()

        # Drop database if exists
        cursor.execute("DROP DATABASE IF EXISTS hotel_db")

        # Create database
        cursor.execute("CREATE DATABASE hotel_db")

        # Use hotel_db
        cursor.execute("USE hotel_db")

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

        # Create hotels table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            hotel_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
            address VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(15) NOT NULL,
            stars INT NOT NULL,
            check_in_time TIME NOT NULL,
            check_out_time TIME NOT NULL
        )""")

        # Create room_types table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_types (
            room_type_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            description VARCHAR(255) NOT NULL,
            price_per_night DECIMAL(10, 2) NOT NULL, 
            capacity INT NOT NULL
        )""")

        # Create rooms table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_number INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
            hotel_id INT NOT NULL, 
            room_type_id INT NOT NULL,
            status VARCHAR(20), 
            FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id), 
            FOREIGN KEY (room_type_id) REFERENCES room_types(room_type_id)
        )""")

        # Create bookings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
            guest_ID INT NOT NULL,
            room_number INT NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (guest_ID) REFERENCES users(users_id),
            FOREIGN KEY (room_number) REFERENCES rooms(room_number)
        )""")

        # Create payment table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment (
            payment_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
            booking_ID INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            payment_date DATE NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            FOREIGN KEY (booking_ID) REFERENCES bookings(booking_ID)
        )""")

        # Insert Admin User
        admin_password = 'adminpassword'
        password = generate_password_hash(admin_password)
        cursor.execute("""INSERT INTO users (email, firstName, lastName, phoneNumber, password_hash, usertype)
                        VALUES ('admin@gmail.com', 'Ad', 'Min', '1231684968', %s, 'admin')""", (password,))

        connection.commit()
        connection.close()

    except mysql.connector.Error as err:
        print("Error:", err)


if __name__ == "__main__":
    create_tables()