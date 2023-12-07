import MySQLdb
import subprocess
import time
import random
import os
from nlp.transfermarktscraper import scraper
import nlp
import sys


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
def check_player_recent_transfer(cursor, player_id):
    query = """
    SELECT stage, latest_timestamp
    FROM transfers
    JOIN players on transfers.player_id = players.player_id
    JOIN
            (
                SELECT
                    transfer_id, MAX(timestamp) AS latest_timestamp
                FROM
                    sources
                JOIN
                    source_transfer ON sources.source_id = source_transfer.source_id
                GROUP BY
                    transfer_id
            ) AS latest_sources ON transfers.transfer_id = latest_sources.transfer_id
    WHERE players.player_id = %s"""

    cursor.execute(query, (player_id,))

    


def check_team_in_database(cursor, team_link):
    cursor.execute("SELECT team_id FROM teams WHERE team_link = %s", (team_link,))
    existing_record = cursor.fetchone()
    
    if existing_record == None:
        return None
    else:
        return existing_record[0]
    
def check_player_in_database(cursor, player_link):
    cursor.execute("SELECT player_id FROM players WHERE player_link = %s", (player_link,))
    existing_record = cursor.fetchone()
    
    if existing_record == None:
        return None
    else:
        return existing_record[0]

def check_nation_in_database(cursor, nation_name):
    cursor.execute("SELECT nation_id FROM nations WHERE nation_name = %s", (nation_name,))
    existing_record = cursor.fetchone()
    
    if existing_record == None:
        return None
    else:
        return existing_record[0]

def check_transfer_in_database(cursor, player_id, team_id):
    cursor.execute("SELECT transfer_id FROM transfers WHERE player_id = %s AND rumoured_team_id = %s", (player_id, team_id))
    existing_record = cursor.fetchone()
    
    if existing_record == None:
        return None
    else:
        return existing_record[0]


def add_player(cursor, player_data, team_id, nation_id):
    query = "INSERT INTO players (player_name, player_link, player_image, player_position, market_value, date_of_birth, current_team_id, nation_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (player_data["player_name"], player_data["player_link"], player_data["player_face_url"], player_data["position"], player_data["market_value"], player_data["date_of_birth"], team_id, nation_id))
    print("Added player {0}".format(player_data["player_name"]))
    sys.stdout.flush()
    return cursor.lastrowid

def add_team(cursor, team_data):
    team_name = team_data["team_name"]
    league_name = team_data["league_name"]
    logo_image = team_data["team_logo_url"]
    team_link = team_data["team_link"]
    try:
        cursor.execute("INSERT INTO teams (team_name, league_name, logo_image, team_link) VALUES (%s, %s, %s, %s)", (team_name, league_name, logo_image, team_link))
        return cursor.lastrowid
        #db.commit()
    except Exception as e:
        print(e)
        print(team_data)
        sys.stdout.flush()
        return None

def add_nation(cursor, nation_data):
    try:
        cursor.execute("INSERT INTO nations (nation_name, nation_flag) VALUES (%s, %s)", (nation_data["name"], nation_data["flag_image"]))
        return cursor.lastrowid
        #db.commit()
    except Exception as e:
        print(e)
        print(nation_data)
        sys.stdout.flush()
        return None

def add_transfer_to_database(cursor, player_id, rumoured_team_id):
    try:
        cursor.execute("INSERT INTO transfers (player_id, rumoured_team_id) VALUES (%s, %s)", (player_id, rumoured_team_id))
        return cursor.lastrowid
    except Exception as e:
        print(e)
        sys.stdout.flush()
        return None

def add_transfer(db, source_id, doc):
    # def get_player_current_team(player_index, doc):
    #     for key, label in doc._.transfers.items():
    #         if key[0] == player_index and label == "plays_for":
    #             return key[1]
    #     return None
    
    def get_rumoured_relations(doc):
        relations = []
        for key, label in doc._.transfers.items():
            if label == "rumoured_to_join":
                relations.append(key)
        return relations
    
    cursor = db.cursor()
    
    database_ids = [-1 for _ in range(len(doc._.ent_groups))]
    for i, normalised_item in enumerate(doc._.normalised_names):
        if normalised_item != -1:
            #if player, checks if there is a current_team
            if normalised_item.item_type == "team":
                team_id = check_team_in_database(cursor, normalised_item.url)
                if team_id == None:
                    team_data = scraper.get_team_info_from_link(normalised_item.url)
                    team_id = add_team(cursor, team_data)
                database_ids[i] = team_id
                    
            elif normalised_item.item_type == "player":
                # current_team_index = get_player_current_team(i, doc)
                # if current_team_index == None or doc._.normalised_names[current_team_index] == -1:
                player_id = check_player_in_database(cursor, normalised_item.url)
                if player_id == None:
                    player_data = scraper.get_player_info_from_link(normalised_item.url)
                    
                    current_team_id = check_team_in_database(cursor, normalised_item.team_url)
                    if current_team_id == None:
                        team_data = scraper.get_team_info_from_link(normalised_item.team_url)
                        current_team_id = add_team(cursor, team_data)
                
                    nation_id = check_nation_in_database(cursor, player_data["nation_name"])
                    if nation_id == None:
                        nation_data = scraper.get_nation_info(player_data["nation_name"])
                        nation_id = add_nation(cursor, nation_data)
                        
                    player_id = add_player(cursor, player_data, current_team_id, nation_id)
                database_ids[i] = player_id
                    
    for relation in get_rumoured_relations(doc):
        player_id = database_ids[relation[0]]
        rumoured_team_id = database_ids[relation[1]]
        if player_id == -1 or rumoured_team_id == -1:
            continue
        transfer_id = check_transfer_in_database(cursor, player_id, rumoured_team_id)
        if transfer_id == None:
            transfer_id = add_transfer_to_database(cursor, player_id, rumoured_team_id)
        try:
            cursor.execute("INSERT INTO source_transfer (source_id, transfer_id) VALUES (%s, %s)", (source_id, transfer_id))
        except:
            print("Source {0} already added to transfer {1}".format(source_id, transfer_id))
            sys.stdout.flush()
            
    db.commit()
    cursor.close()
        
    
#TODO delete source_transfer before deleting transfer
def delete_old_transfers(db, time_days):
    cursor = db.cursor()
    
    time_seconds = time_days * 24 * 60 * 60


    query = """SELECT transfer_id FROM transfers
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
    transfer_ids = cursor.fetchall()

    for transfer_id in transfer_ids:
        transfer_id = transfer_id[0]
        delete_transfer(cursor, transfer_id)
    
    db.commit()
    cursor.close()

def delete_transfer(cursor, transfer_id):
    query = """
    DELETE FROM source_transfer
    WHERE transfer_id = %s"""

    cursor.execute(query, (transfer_id,))

    query = """
    DELETE FROM transfers
    WHERE transfer_id = %s"""

    cursor.exceute(query, (transfer_id,))
    
def update_player_data(db):
    cursor = db.cursor()

    query = """
    SELECT 
        player_id,
        player_link,
        teams.team_link,
        nations.nation_name,
        player_name,
        player_image,
        player_position,
        market_value,
        date_of_birth
    FROM players
    JOIN teams on players.current_team_id = teams.team_id
    JOIN nations on players.nation_id = nations.nation_id"""

    cursor.execute(query)
    all_players = cursor.fetchall() #[player_id, player_link, team_link, nation_name, ...]

    query = """
    UPDATE players
    SET
        team_id = %s,
        nation_id = %s,
        player_name = %s,
        player_image = %s,
        player_position = %s,
        market_value = %s,
        date_of_birth = %s,
    WHERE
        player_id = %s
    """

    for player in all_players:
        player_id = player[0]
        player_link = player[1]
        team_link = player[2]
        nation_name = player[3]
        player_info = scraper.get_player_info_from_link(player_link)
        if player_info["nation_name"] != nation_name:
            nation_id = check_nation_in_database(cursor, nation_name)
            if nation_id == None:
                nation_data = scraper.get_nation_info(nation_name)
                nation_id = add_nation(cursor, nation_data)
        if player_info["team_link"] != team_link:
            team_id = check_team_in_database(cursor, team_link)
            if team_id == None:
                team_data = scraper.get_team_info_from_link(team_link)
                team_id = add_team(cursor, team_data)

        cursor.execute(query, (team_id, nation_id, player_info["player_face_url"], player_info["position"], player_info["market_value"], player_info["date_of_birth"], player_id))

    db.commit()
    cursor.close()




def update_market_values(db):
    cursor = db.cursor()
    
    query = """
    SELECT player_id, player_name, team_name FROM players
    JOIN teams ON players.current_team_id = teams.team_id
    """
    
    query2 = """
    SELECT player_id, player_name, team_name FROM players,teams 
    WHERE players.current_team_id = teams.team_id
    """
    
    cursor.execute(query)
    all_players = cursor.fetchall()
    
    for player in all_players:
        player_id = player[0]
        player_name = player[1]
        current_team_name = player[2]
        
        #TODO change to use link
        player_market_value = scraper.get_player_info(player_name, current_team_name)[5]
        
        cursor.execute("UPDATE players SET market_value = %s WHERE player_id = %s", (player_market_value, player_id))
        
        
    db.commit()
    cursor.close()

def update_transfers(mysql_user, mysql_password, mysql_port, time_wait):
    
    subprocess.run(["/app/transfer_sources/twitter/get_tweets.bin", mysql_user, mysql_password, str(mysql_port), str(time_wait)], check=True, cwd="/app/transfer_sources/twitter")

    db = MySQLdb.connect(host="mysql", user=mysql_user, passwd=mysql_password, port=mysql_port, db="transfer_data")

    #Gets the tweets from the database
    sources = get_new_sources(db, time_wait)
    for source in sources: #source: [source_id, text, timestamp]
        #nlp - transfer_data: [bool is_rumour, player_names, current_team_names, rumoured_team_names, stage, bid]
        transfer_data_doc = nlp.interpret_source(source[1])
        
        print(transfer_data_doc)
        sys.stdout.flush()
        if transfer_data_doc is not None:            
            add_transfer(db, source[0], transfer_data_doc)
        else:
            delete_source(db, source[0])
            
    #Checking if any transfers have been confirmed by checking if transfermarkt has updated the player's current team
    #TODO use link
    cursor = db.cursor()
    query = """
    SELECT transfer_id, player_link, team_link
    FROM transfers
    JOIN players on transfers.player_id = players.player_id
    JOIN teams on transfers.rumoured_team_id = team_id
    """

    cursor.execute(query)
    all_transfers = cursor.fetchall()
    
    for transfer_data in all_transfers:
        try:
            current_team = scraper.get_player_info_from_link(transfer_data[1])["team_link"]
            if current_team == transfer_data[2]:
                cursor.execute("UPDATE transfers SET stage='done_official' WHERE transfer_id = {0}".format(transfer_data[0]))
                query = """
                SELECT transfer_id FROM transfers
                JOIN players on transfers.player_id = players.player_id
                JOIN teams on transfers.rumoured_team_id = team_id
                WHERE players.player_link = %s AND teams.team_link != %s"""
                cursor.execute(query, (transfer_data[1], transfer_data[2]))
                transfer_ids = cursor.fetchall()
                for transfer_id in transfer_ids:
                    delete_transfer(cursor, transfer_id)
                
        except:
            print("Transfer with ID {0} involving player {1} and team {2} not found on transfermarkt - deal is not official".format(transfer_data[0], transfer_data[1], transfer_data[2]))
            
    delete_old_transfers(db, 7)
            
    db.commit()
    cursor.close()
    db.close()

def main():
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))
    TIME_WAIT = int(os.environ.get("TIME_WAIT"))

    update_count = 0
    MONTH_IN_SECONDS = int(25920000/TIME_WAIT)
    
    print("Starting update_database.py")
    sys.stdout.flush()
    
    try:
        with open("prev_time.txt", "r") as f:
            prev_time = int(f.read())
    except:
        prev_time = 0
        with open("prev_time.txt", "w") as f:
            f.write(str(prev_time))
    
    time_gap_random = random.randint(TIME_WAIT-200, TIME_WAIT+200)
    #Calls in periodic intervals determined by the TIME_WAIT environment variable
    while True:
        current_timestamp = int(time.time())
        #TODO update market values
        
        if current_timestamp - prev_time >= time_gap_random:
            prev_time = current_timestamp
            with open("prev_time.txt", "w") as f:
                f.write(str(prev_time))
            update_transfers(MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, time_gap_random)
            time_gap_random = random.randint(TIME_WAIT-200, TIME_WAIT+200)

            update_count += 1
            if update_count >= MONTH_IN_SECONDS:
                update_count = 0
                db = MySQLdb.connect(host="mysql", user=MYSQL_USER, passwd=MYSQL_PASSWORD, port=MYSQL_PORT, db="transfer_data")
                update_player_data(db)
                #update_player_data()
        
        time.sleep(1)
        
if __name__ == "__main__":
    main()