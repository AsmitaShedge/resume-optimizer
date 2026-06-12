import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        port="3307",
        password="",
        database="resume_optimizer"
    )