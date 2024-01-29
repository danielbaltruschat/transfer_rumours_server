import MySQLdb
import database_functions
import argparse

parser = argparse.ArgumentParser(description='Delete transfers for contract renewals / players transferring to the same club.')
parser.add_argument('-u', '--user', help='MySQL username', required=True)
parser.add_argument('-p', '--password', help='MySQL password', required=True)
parser.add_argument('-P', '--port', help='MySQL port', type=int, required=True)

args = parser.parse_args()

db = MySQLdb.connect(host="mysql", user=args.user, passwd=args.password, port=args.port, db="transfer_data")

query = """SELECT transfer_id
FROM transfers
JOIN players on transfers.player_id = players.player_id
WHERE transfers.rumoured_team_id = players.current_team_id"""

cursor = db.cursor()
cursor.execute(query)
transfer_ids = cursor.fetchall()

for transfer_id in transfer_ids:
    database_functions.delete_transfer(cursor, transfer_id[0])
    
db.commit()
cursor.close()
db.close()