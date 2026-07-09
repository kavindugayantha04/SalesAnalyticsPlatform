from db_connection import get_connection

connection = get_connection()

if connection:
    print("Connection Test Passed!")
    connection.close()
else:
    print("Connection Test Failed!")