import sys
import apsw 
from apsw import Error
import hashlib
import secrets

def initMessageDatabase():
    try:     
        conn = apsw.Connection('./messages.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id integer PRIMARY KEY, 
            sender TEXT NOT NULL,
            message TEXT NOT NULL);''')
        c.execute('''CREATE TABLE IF NOT EXISTS announcements (
            id integer PRIMARY KEY, 
            author TEXT NOT NULL,
            text TEXT NOT NULL);''')
        
        #Creating table for usernames and hashed passwords.
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT NOT NULL,
            salt TEXT NOT NULL);''')
        
        #Inserting the users with their hashed passwords. Do this 1 time to get it in the database, then comment out the code. 
        #c.execute('INSERT INTO users (username, password, salt) VALUES (?, ?, ?)', ('Bob', '6c2bc66fd876d2fcc6d370ab859a0f2fda36e320666a34228eacad0e2db9a73b4a8a6ffed523fac5406dc9d6726f3b242b1efdb2639100072758111d8528e967', '6f6c57b6e5062d0e98943cccaf4a276f'))
        #c.execute('INSERT INTO users (username, password, salt) VALUES (?, ?, ?)', ('Alice', 'eff6f831ca7c50664f264e25aac3b19075a43932b56ca7b626cacf48b3bad2fb0b1e918f29b0bc90bfc1bd57022b06a98e88460a6b87d20fdf3ce4a68ec786ae', 'c62459e644bb42574365ccadb7e98bf9'))
        
        return conn
    except Error as e:
        print(e)
        sys.exit(1)