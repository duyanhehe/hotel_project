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
            peak_season_price DECIMAL(10, 2) NOT NULL, 
            off_peak_price DECIMAL(10, 2) NOT NULL, 
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
            total_price DECIMAL(10, 2) NOT NULL,
            booking_date DATE NOT NULL,
            FOREIGN KEY (users_id) REFERENCES users(users_id) ON DELETE CASCADE,
            FOREIGN KEY (room_id) REFERENCES room(room_id) ON DELETE CASCADE
        )""")

        # Create trigger to update room status to "unavailable" when a booking is inserted
        cursor.execute("""
        CREATE TRIGGER update_room_status
        AFTER INSERT ON booking
        FOR EACH ROW
        BEGIN
            UPDATE room
            SET status = 'Unavailable'
            WHERE room_id = NEW.room_id;
        END;
        """)

        # Create payment table
        # cursor.execute("""
        # CREATE TABLE IF NOT EXISTS payment (
        #     payment_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
        #     booking_ID INT NOT NULL,
        #     amount DECIMAL(10, 2) NOT NULL,
        #     payment_date DATE NOT NULL,
        #     payment_method VARCHAR(50) NOT NULL,
        #     FOREIGN KEY (booking_ID) REFERENCES bookings(booking_ID)
        # )""")

        #################       INSERT MOCK DATA        #################
        # Insert Admin User
        admin_password = 'adminpassword'
        password = generate_password_hash(admin_password)
        cursor.execute("""INSERT INTO users (email, firstName, lastName, phoneNumber, password_hash, usertype)
                        VALUES ('admin@gmail.com', 'Ad', 'Min', '1231684968', %s, 'admin')""", (password,))
        
        # Insert User
        user_password = generate_password_hash('password')
        cursor.execute("""INSERT INTO users (email, firstName, lastName, phoneNumber, password_hash, usertype)
                        VALUES ('test@gmail.com', 'User', 'Test', '123123123', %s, 'standard')""", (user_password,))

        # Insert hotels
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Aberdeen', 'Aberdeen Hotel', 'aberdeenHotel@gmail.com', '999999999', 90)""")
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Belfast', 'Belfast Hotel', 'belfastHotel@gmail.com', '888888888', 80)""")
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Birmingham', 'Birmingham Hotel', 'birminghamHotel@gmail.com', '777777777', 110)""")
        cursor.execute("""INSERT INTO hotel (city, hotel_name, email, phone, capacity)
                    VALUES ('Bristol', 'Bristol Hotel', 'bristolHotel@gmail.com', '666666666', 100)""")
        
        # Insert rooms into aberdeen hotel
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (1, 'Standard', 'Wifi, TV', 59.99, 39.99, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (1, 'Double', 'Wifi, TV, mini-bar', 90.00, 70.00, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (1, 'Family', 'Wifi, TV, mini-bar, breakfast', 200.00, 120.00, 'Available')""")
        # Insert rooms into belfast hotel
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (2, 'Standard', 'Wifi, TV, AC', 49.99, 29.99, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (2, 'Double', 'Wifi, TV, mini-bar, AC', 80.00, 60.00, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (2, 'Family', 'Wifi, TV, AC, mini-bar, breakfast', 190.00, 110.00, 'Available')""")
        # Insert rooms into birmingham hotel
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (3, 'Standard', 'Wifi, TV, AC', 64.99, 44.99, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (3, 'Double', 'Wifi, TV, mini-bar, AC', 95.00, 75.00, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (3, 'Family', 'Wifi, TV, AC, mini-bar, breakfast', 205.00, 125.00, 'Available')""")
        # Insert rooms into bristol hotel
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (4, 'Standard', 'Wifi, TV, AC', 59.99, 39.99, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (4, 'Double', 'Wifi, TV, mini-bar, AC', 90.00, 70.00, 'Available')""")
        cursor.execute("""INSERT INTO room (hotel_id, room_type, features, peak_season_price, off_peak_price, status)
                       VALUES (4, 'Family', 'Wifi, TV, AC, mini-bar, breakfast', 200.00, 120.00, 'Available')""")

        # Insert into booking
        cursor.execute("""INSERT INTO booking (users_id, room_id, check_in_date, check_out_date, total_price, booking_date)
                       VALUES (2, 4, '2024-06-25', '2024-06-28', 49.99, '2024-04-21')""")

        connection.commit()
        connection.close()

    except mysql.connector.Error as err:
        print("Error:", err)


if __name__ == "__main__":
    create_tables()