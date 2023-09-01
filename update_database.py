import MySQLdb
import subprocess
import time
import random
import os
from transfermarktscraper import normalise_data
from transfermarktscraper import scraper
import sys
import nlp


def get_new_sources(db, time_wait):
    cursor = db.cursor()
    
    prev_time = int(time.time()) - time_wait

    cursor.execute("SELECT source_id, text, timestamp FROM sources WHERE timestamp > %s", (prev_time,))
    sources = cursor.fetchall()
    
    #db.close()
    return sources
    
def delete_source(db, source_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM sources WHERE source_id = %s", (source_id,))
    db.commit()
    
    
'''
Format:
    player_data = [player_name, player_face_url]
    current_team_data = [current_team_name, current_team_league, current_team_logo_url]
    rumoured_team_data = [rumoured_team_name, rumoured_team_league, rumoured_team_logo_url]
'''
def add_transfer(db, source_id, player_data, current_team_data, rumoured_team_data, stage):
    #Initially sets in_transfer to True and sets it to False if the player or one of the teams is not already in the database
    in_transfers = True
    
    #Connects to the database
    #db = MySQLdb.connect(host="mysql", user=mysql_user, passwd=mysql_password, port=mysql_port, db="transfer_data")
    cursor = db.cursor()
    
    #Checks if teams are already in the database
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
            in_transfers = False
        else:
            team_ids.append(existing_record[0])
                        
    
    #Checks if the player is already in the database
    cursor.execute("SELECT player_id FROM players WHERE player_name = %s AND current_team_id = %s", (player_data[0], team_ids[0]))
    existing_record = cursor.fetchone()
    if existing_record == None:
        in_transfers = False
        cursor.execute("INSERT INTO players (player_name, player_image, current_team_id) VALUES (%s, %s, %s)", (*player_data, team_ids[0]))
        print("Added player {0}".format(player_data[0]))
        sys.stdout.flush()
        player_id = cursor.lastrowid
    else:
        player_id = existing_record[0]
        
    #Checks if the transfer is already in the database, knows not in database if either player or teams are not in database - saves a query
    if not in_transfers:
        cursor.execute("INSERT INTO transfers (player_id, rumoured_team_id, stage) VALUES (%s, %s, %s)", (player_id, team_ids[1], stage))
        transfer_id = cursor.lastrowid
    else:
        cursor.execute("SELECT transfer_id FROM transfers WHERE player_id = %s AND rumoured_team_id = %s", (player_id, team_ids[1]))
        existing_record = cursor.fetchone()
        if existing_record == None:
            cursor.execute("INSERT INTO transfers (player_id, rumoured_team_id, stage) VALUES (%s, %s, %s)", (player_id, team_ids[1], stage))
            transfer_id = cursor.lastrowid
        else:
            transfer_id = existing_record[0]
            #updates stage of transfer if the transfer is already in the database and there is new info on it
            if stage != "unknown":
                cursor.execute("UPDATE transfers SET stage = %s WHERE transfer_id = %s", (stage, transfer_id))
    
    #Adds the source to the transfer
    #cursor.execute("UPDATE sources SET transfer_id = {0} WHERE source_id = {1}".format(transfer_id, source_id))
    try:
        cursor.execute("INSERT INTO source_transfer (source_id, transfer_id) VALUES (%s, %s)", (source_id, transfer_id))
    except:
        print("Source {0} already added to transfer {1}".format(source_id, transfer_id))
        sys.stdout.flush()
    
    db.commit()
    cursor.close()
    #db.close()
    
def delete_old_transfers(db, time_days):
    cursor = db.cursor()
    
    time_seconds = time_days * 24 * 60 * 60
    
    query = """DELETE FROM transfers
        WHERE transfer_id IN (
            SELECT transfer_id
            FROM (
                SELECT transfer_id, MAX(timestamp) AS latest_timestamp
                FROM sources
                JOIN source_transfer ON sources.source_id = source_transfer.source_id
                GROUP BY transfer_id
            ) AS latest_sources
            WHERE latest_timestamp < %s)"""
    
    #TODO
    query2 = """
    DELETE FROM transfers
    WHERE (
        SELECT transfer_id, MAX(timestamp) AS latest_timestamp
        FROM sources, source_transfer
        WHERE sources.source_id = source_transfer.source_id
        GROUP BY transfer_id
    )
    WHERE latest_timestamp < %s
    """
    
    
    cursor.execute(query, (int(time.time()) - time_seconds,))
    
    db.commit()
    cursor.close()

def update_database(mysql_user, mysql_password, mysql_port, time_wait):
    
    subprocess.run(["/app/transfer_sources/twitter/get_tweets.bin", mysql_user, mysql_password, str(mysql_port), str(time_wait)], check=True, cwd="/app/transfer_sources/twitter")

    db = MySQLdb.connect(host="mysql", user=mysql_user, passwd=mysql_password, port=mysql_port, db="transfer_data")

    #Gets the tweets from the database
    sources = get_new_sources(db, time_wait)
    for source in sources: #source: [source_id, text, timestamp]
        #nlp - transfer_data: [bool is_rumour, player_names, current_team_names, rumoured_team_names, stage, bid]
        transfer_data = nlp.interpret_source(source[1])
        
        print(transfer_data)
        sys.stdout.flush()
        if transfer_data[0]:
            try:
                transfer_data[1], transfer_data[2], transfer_data[3] = normalise_data.normalise_data(transfer_data[1], transfer_data[2], transfer_data[3])
            except:
                delete_source(db, source[0])
                continue

            rumoured_team_data = scraper.get_team_info(transfer_data[3][0])
            
            #checks if there is a current team identified from the nlp process
            if len(transfer_data[2]) != 0:
                current_team_data = scraper.get_team_info(transfer_data[2][0])
                player_name, _, player_image = scraper.get_player_info(transfer_data[1][0], current_team_data[0])
                player_data = [player_name, player_image]
            else:
                player_name, current_team, player_image = scraper.get_player_info(transfer_data[1][0])
                player_data = [player_name, player_image]
                current_team_data = scraper.get_team_info(current_team)
            
            add_transfer(db, source[0], player_data, current_team_data, rumoured_team_data, transfer_data[4])
            
        else:
            delete_source(db, source[0])
            
    #Checking if any transfers have been confirmed by checking if transfermarkt has updated the player's current team
    cursor = db.cursor()
    cursor.execute("SELECT transfer_id, player_name, team_name FROM transfers, players, teams WHERE transfers.player_id = players.player_id AND transfers.rumoured_team_id = teams.team_id")
    all_transfers = cursor.fetchall()
    
    for transfer_data in all_transfers:
        try:
            current_team = scraper.get_players_from_search_results(transfer_data[1], transfer_data[2])[0][1]
            if current_team == transfer_data[2]:
                cursor.execute("UPDATE transfers SET stage='done_official' WHERE transfer_id = {0}".format(transfer_data[0]))
        except:
            print("Transfer with ID {0} involving player {1} and team {2} not found on transfermarkt - deal is not official".format(transfer_data[0], transfer_data[1], transfer_data[2]))
            
    delete_old_transfers(db, 7)
            
    db.commit()
    cursor.close()
    db.close()

def main():
    mysql_user = os.environ.get("MYSQL_USER")
    mysql_password = os.environ.get("MYSQL_PASSWORD")
    mysql_port = int(os.environ.get("MYSQL_PORT"))
    time_wait = int(os.environ.get("TIME_WAIT"))
    
    print("Starting update_database.py")
    sys.stdout.flush()
    
    try:
        with open("prev_time.txt", "r") as f:
            prev_time = int(f.read())
    except:
        prev_time = 0
        with open("prev_time.txt", "w") as f:
            f.write(str(prev_time))
    
    time_gap_random = random.randint(time_wait-200, time_wait+200)
    #Calls in periodic intervals determined by the TIME_WAIT environment variable
    while True:
        current_timestamp = int(time.time())
        if current_timestamp - prev_time >= time_gap_random:
            prev_time = current_timestamp
            with open("prev_time.txt", "w") as f:
                f.write(str(prev_time))
            update_database(mysql_user, mysql_password, mysql_port, time_gap_random)
            time_gap_random = random.randint(time_wait-200, time_wait+200)
        
        time.sleep(1)
        
if __name__ == "__main__":
    main()