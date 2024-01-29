import MySQLdb
import database_functions
import argparse

parser = argparse.ArgumentParser(description='Delete transfer with given transfer id.')
parser.add_argument('-t', '--transfer_id', help='Transfer id', required=True)
parser.add_argument('-u', '--user', help='MySQL username', required=True)
parser.add_argument('-p', '--password', help='MySQL password', required=True)
parser.add_argument('-P', '--port', help='MySQL port', type=int, required=True)

args = parser.parse_args()

db = MySQLdb.connect(host="mysql", user=args.user, passwd=args.password, port=args.port, db="transfer_data")
cursor = db.cursor()
database_functions.delete_transfer(cursor, args.transfer_id)