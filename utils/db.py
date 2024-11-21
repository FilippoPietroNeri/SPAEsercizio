import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="mysql-3c32f481-filippopietro-5cb4.l.aivencloud.com",
            port=18611,
            database="polimiSeminari",
            user="avnadmin",
            password="AVNS_0zhF2XOUi-BH-EUduwz"
        )
        if connection.is_connected():
            print("Connesso a MySQL")
        return connection
    except Error as e:
        print(f"Errore nella connessione: {e}")
        return None
