import MySQLdb
import database_functions
import json
import argparse

parser = argparse.ArgumentParser(description='Delete teams that are part of a list of names from the database. List of names given in a JSON file. \n\n THIS ALSO DELETES ANY TRANSFERS THAT INVOLVE THE DELETED TEAMS.')
parser.add_argument('-f', '--file', help='JSON file containing list of names to delete', required=True)
parser.add_argument('-u', '--user', help='MySQL username', required=True)
parser.add_argument('-p', '--password', help='MySQL password', required=True)
parser.add_argument('-P', '--port', help='MySQL port', type=int, required=True)

args = parser.parse_args()

db = MySQLdb.connect(host="mysql", user=args.user, passwd=args.password, port=args.port, db="transfer_data")

# Get list of names to delete
with open(args.file) as f:
    teams_to_delete = json.load(f)

teams_to_delete_regex = "|".join(teams_to_delete)


query_get_teams = """SELECT team_id FROM teams WHERE team_name REGEXP %s"""
cursor = db.cursor()
cursor.execute(query_get_teams, (teams_to_delete_regex,))
teams_ids_to_delete = cursor.fetchall()

query_get_transfers = """SELECT transfer_id FROM transfers WHERE rumoured_team_id = %s"""

for team in teams_ids_to_delete:
    cursor.execute(query_get_transfers, (team[0],))
    transfers_to_delete = cursor.fetchall()
    for transfer in transfers_to_delete:
        database_functions.delete_transfer(cursor, transfer[0])
    database_functions.delete_team(cursor, team[0])

cursor.close()    
db.commit()
db.close()

print("Teams Deleted")