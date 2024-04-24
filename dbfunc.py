import mysql.connector
from mysql.connector import errorcode

hostname    = "127.0.0.1"
db          = "hotel_db"
username    = "root"
passwd  = "1234"
    
def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                            user=username,
                            db = db,
                            password=passwd)  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else:  
        return conn