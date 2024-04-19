DROP DATABASE IF EXISTS hotel_db;
CREATE DATABASE hotel_db;
USE hotel_db;

CREATE TABLE users(
users_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
email VARCHAR(120) NOT NULL UNIQUE,
firstName VARCHAR(50) NOT NULL,
lastName VARCHAR(50) NOT NULL,
phoneNumber VARCHAR(15) NOT NULL UNIQUE,
password_hash VARCHAR(255),
usertype VARCHAR(8) DEFAULT 'standard'
);

CREATE TABLE admin_users(
admin_users_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
email VARCHAR(120) NOT NULL UNIQUE,
firstName VARCHAR(50) NOT NULL,
lastName VARCHAR(50) NOT NULL,
phoneNumber VARCHAR(15) NOT NULL UNIQUE,
password_hash VARCHAR(255),
usertype VARCHAR(8) DEFAULT 'admin'
);

INSERT INTO admin_users VALUES (1, "admin@gmail.com", "ad", "min", "99999999", "password")


CREATE TABLE hotels (
    hotel_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
    address VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    stars INT NOT NULL,
    check_in_time TIME NOT NULL,
    check_out_time TIME NOT NULL
);


CREATE TABLE room_types (
    type_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    price_per_night DECIMAL(10, 2) NOT NULL, 
    capacity INT NOT NULL
);


CREATE TABLE rooms (
    room_number INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
    hotel_id INT NOT NULL, 
    type_id INT NOT NULL,
    status VARCHAR(20), 
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id), 
    FOREIGN KEY (type_id) REFERENCES room_types(type_id)
);


CREATE TABLE bookings (
    booking_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    guest_ID INT NOT NULL,
    room_number INT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (guest_ID) REFERENCES users(users_id),
    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
);

CREATE TABLE payment (
    payment_ID INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    booking_ID INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    FOREIGN KEY (booking_ID) REFERENCES bookings(booking_ID)
);