import MySQLdb
import subprocess
import time
import random
import os
from nlp.transfermarktscraper import scraper
from database_functions import *
import nlp
import sys

def get_new_sources(cursor, time_wait):
    
    prev_time = int(time.time()) - time_wait

    cursor.execute("SELECT source_id, text, timestamp FROM sources WHERE timestamp > %s", (prev_time,))
    sources = cursor.fetchall()
    
    #db.close()
    return sources

def add_official_transfer(cursor, player_id, team_link):
    team_id = check_team_in_database(cursor, team_link)
    if team_id == None:
        team_data = scraper.get_team_info_from_link(team_link)
        team_id = add_team(cursor, team_data)
    transfer_id = add_transfer_to_database(cursor, player_id, team_id)
    cursor.execute("UPDATE transfers SET stage='done_official' WHERE transfer_id = {0}".format(transfer_id))
    bump_transfer(cursor, transfer_id)
    

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
            WHERE latest_timestamp < %s AND (stage = 'done_official' OR stage = 'deal_off_official'))"""
    
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


def add_transfer(cursor, source_id, doc):
        
    def get_rumoured_relations(doc):
        relations = []
        for key, label in doc._.transfers.items():
            if label == "rumoured_to_join":
                relations.append(key)
        return relations
    
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
        
        player_item = doc._.normalised_names[relation[0]]
        rumoured_team_item = doc._.normalised_names[relation[1]]
        
        if player_id == -1 or rumoured_team_id == -1:
            continue
        if player_item.team_url == rumoured_team_item.url:
            continue

        transfer_id = check_transfer_in_database(cursor, player_id, rumoured_team_id)
        if transfer_id == None:
            transfer_id = add_transfer_to_database(cursor, player_id, rumoured_team_id)
        try:
            cursor.execute("INSERT INTO source_transfer (source_id, transfer_id) VALUES (%s, %s)", (source_id, transfer_id))
        except:
            print("Source {0} already added to transfer {1}".format(source_id, transfer_id))
            sys.stdout.flush()
            
        
    
def update_player_data(db):
    cursor = db.cursor()

    query = """
    SELECT 
        players.player_id,
        player_link,
        teams.team_link,
        nations.nation_name,
        player_name,
        player_image,
        player_position,
        market_value,
        date_of_birth,
        current_team_id,
        players.nation_id
    FROM players
    JOIN teams ON players.current_team_id = teams.team_id
    JOIN nations ON players.nation_id = nations.nation_id
    JOIN transfers ON players.player_id = transfers.player_id
    WHERE transfers.stage != 'done_official' AND transfers.stage != 'deal_off_official'"""

    cursor.execute(query)
    all_players = cursor.fetchall() #[player_id, player_link, team_link, nation_name, ...]

    query = """
    UPDATE players
    SET
        current_team_id = %s,
        nation_id = %s,
        player_name = %s,
        player_image = %s,
        player_position = %s,
        market_value = %s,
        date_of_birth = %s
    WHERE
        player_id = %s
    """

    for player in all_players:
        try:
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
            else:
                nation_id = player[10]
            if player_info["team_link"] != team_link:
                team_id = check_team_in_database(cursor, team_link)
                if team_id == None:
                    team_data = scraper.get_team_info_from_link(team_link)
                    team_id = add_team(cursor, team_data)
            else:
                team_id = player[9]
        except Exception as e:
            print(f"Failed to get player info for link {player_link}")
            print(e)
            continue

        cursor.execute(query, (team_id, nation_id, player_info["player_name"], player_info["player_face_url"], player_info["position"], player_info["market_value"], player_info["date_of_birth"], player_id))

    db.commit()
    cursor.close()



def update_transfers(mysql_user, mysql_password, mysql_port, time_wait):
    
    subprocess.run(["/app/transfer_sources/twitter/get_tweets.bin", mysql_user, mysql_password, str(mysql_port), str(time_wait)], check=True, cwd="/app/transfer_sources/twitter")

    db = MySQLdb.connect(host="mysql", user=mysql_user, passwd=mysql_password, port=mysql_port, db="transfer_data")
    cursor = db.cursor()

    #Gets the tweets from the database
    sources = get_new_sources(cursor, time_wait)
    for source in sources: #source: [source_id, text, timestamp]
        #nlp - transfer_data: [bool is_rumour, player_names, current_team_names, rumoured_team_names, stage, bid]
        try:
            text = str(source[1])
            transfer_data_doc = nlp.interpret_source(text)
        except Exception as e:
            print(e)
            transfer_data_doc = None
        
        print(transfer_data_doc)
        sys.stdout.flush()
        if transfer_data_doc is not None:            
            add_transfer(cursor, source[0], transfer_data_doc)
        else:
            try:
                delete_source(cursor, source[0])
            except Exception as e:
                print(e)
            
        db.commit()
            
    #Checking if any transfers have been confirmed by checking if transfermarkt has updated the player's current team
    
    # query = """
    # SELECT transfer_id, player_link, rumoured_team.team_link, current_team.team_link
    # FROM transfers
    # JOIN players on transfers.player_id = players.player_id
    # JOIN teams rumoured_team on transfers.rumoured_team_id = teams.team_id
    # JOIN teams current_team on players.current_team_id = current_team.team_id
    # WHERE stage IS NULL
    # """
    
    query = """SELECT player_id, player_link, team_link
    FROM players
    JOIN teams ON players.current_team_id = teams.team_id
    WHERE player_id IN (
        SELECT player_id
        FROM transfers
        WHERE stage IS NULL
    )"""

    cursor.execute(query)
    #all_transfers = cursor.fetchall()
    all_players = cursor.fetchall()
    
    for player in all_players:
        try:
            current_team = scraper.get_player_info_from_link(player[1])["team_link"]
        except:
            print(f"Failed to get current team for link {player[1]}")
            continue
        if current_team != player[2]:
            query1 = """SELECT transfer_id
            FROM transfers
            JOIN teams ON transfers.rumoured_team_id = teams.team_id
            WHERE player_id = %s AND team_link = %s AND stage IS NULL"""
            query2 = """SELECT transfer_id
            FROM transfers
            JOIN teams ON transfers.rumoured_team_id = teams.team_id
            WHERE player_id = %s AND team_link != %s AND stage IS NULL"""
                        
            cursor.execute(query2, (player[0], current_team))
            transfer_ids = cursor.fetchall()
            for transfer_id in transfer_ids:
                cursor.execute("UPDATE transfers SET stage='deal_off_official' WHERE transfer_id = {0}".format(transfer_id[0]))
                bump_transfer(cursor, transfer_id[0])
                
            cursor.execute(query1, (player[0], current_team))
            transfer_id = cursor.fetchone()
            if transfer_id != None:
                cursor.execute("UPDATE transfers SET stage='done_official' WHERE transfer_id = {0}".format(transfer_id[0]))
                bump_transfer(cursor, transfer_id[0])
            else:
                add_official_transfer(cursor, player[0], current_team)
                
                
                 
    delete_old_transfers(db, 7)
            
    db.commit()
    cursor.close()
    db.close()

def main():
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))
    TIME_WAIT = int(os.environ.get("TIME_WAIT"))

    update_count = int(25920000/TIME_WAIT) + 1
    MONTH = int(25920000/TIME_WAIT)
    
    print("Starting update_database.py")
    sys.stdout.flush()
    
    try:
        with open("timings/prev_time.txt", "r") as f:
            prev_time = int(f.read())
    except Exception as e:
        print(e)
        prev_time = 0
        with open("timings/prev_time.txt", "w") as f:
            f.write(str(prev_time))
    
    time_gap_random = random.randint(TIME_WAIT-200, TIME_WAIT+200)
    #Calls in periodic intervals determined by the TIME_WAIT environment variable
    while True:
        current_timestamp = int(time.time())
        
        if current_timestamp - prev_time >= time_gap_random:
            prev_time = current_timestamp
                        
            with open("timings/prev_time.txt", "w") as f:
                f.write(str(prev_time))
            update_transfers(MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, time_gap_random)
            time_gap_random = random.randint(TIME_WAIT-200, TIME_WAIT+200)

            update_count += 1
            if update_count >= MONTH:
                db = MySQLdb.connect(host="mysql", user=MYSQL_USER, passwd=MYSQL_PASSWORD, port=MYSQL_PORT, db="transfer_data")
                update_count = 0
                update_player_data(db)
                db.close()
        
        time.sleep(1)
        
if __name__ == "__main__":
    main()