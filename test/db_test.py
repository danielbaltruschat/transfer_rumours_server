import MySQLdb

connection = MySQLdb.connect(host="localhost", user="root", passwd="secure_password", port=3306, db="transfer_data")

cursor = connection.cursor()
cursor.execute("SELECT * FROM players")
print(cursor.fetchall())
cursor.close()