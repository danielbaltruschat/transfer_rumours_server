import MySQLdb
import sys

db = MySQLdb.connect(host="localhost", user="root", passwd="secure_password", port=3306, db="transfer_data")

def add_transfer(db, current_team_data, rumoured_team_data):
    #Initially sets in_transfer to True and sets it to False if the player or one of the teams is not already in the database
    
    #Connects to the database
    #db = MySQLdb.connect(host="mysql", user=mysql_user, passwd=mysql_password, port=mysql_port, db="transfer_data")
    cursor = db.cursor()
    
    #Checks if teams are already in the database
    all_team_data = [current_team_data, rumoured_team_data]
    team_ids = [] #team id will have format [current_team_id, rumoured_team_id] after for loop
    for i in range(2):
        team_data = all_team_data[i]
        #cursor.execute("SELECT team_id FROM teams WHERE team_name = '{0}' AND league_name = '{1}'".format(team_data[0], team_data[1]))
        all_team_data = [current_team_data, rumoured_team_data]
    team_ids = [] #team id will have format [current_team_id, rumoured_team_id] after for loop
    for i in range(2):
        team_data = all_team_data[i]
        #cursor.execute("SELECT team_id FROM teams WHERE team_name = '{0}' AND league_name = '{1}'".format(team_data[0], team_data[1]))
        cursor.execute("SELECT team_id FROM teams WHERE team_name = %s AND league_name = %s", (team_data[0], team_data[1]))
        existing_record = cursor.fetchone()
        
        if existing_record == None:
            try:
                cursor.execute("INSERT INTO teams (team_name, league_name, logo_image) VALUES (%s, %s, %s)", (team_data[0], team_data[1], team_data[2]))
            except Exception as e:
                print(e)
                print(team_data)
                sys.stdout.flush()
                
                
            print("Added team {0}".format(team_data[0]))
            sys.stdout.flush()
            team_ids.append(cursor.lastrowid)
        else:
            team_ids.append(existing_record[0])
    
    db.commit()
    cursor.close()
    
add_transfer(db, ["Al-Hilal SFC", "Saudi Pro League", "https://tmssl.akamaized.net/images/wappen/head/1114.png?lm=1661723154"], ["Al Hilal SFC", "Saudi Pro League", "https://tmssl.akamaized.net/images/wappen/head/1114.png?lm=1661723154"])