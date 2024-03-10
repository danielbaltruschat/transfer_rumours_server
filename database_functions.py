import MySQLdb
import sys
import time

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

def check_transfer_in_database(cursor, player_id, rumoured_team_id):
    cursor.execute("SELECT transfer_id FROM transfers WHERE player_id = %s AND rumoured_team_id = %s", (player_id, rumoured_team_id))
    existing_record = cursor.fetchone()
    
    if existing_record == None:
        return None
    else:
        return existing_record[0]

def add_player(cursor, player_data, team_id, nation_id): #player_data is a dictionary
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
    except Exception as e:
        print(e)
        print(team_data)
        sys.stdout.flush()
        return None

def add_nation(cursor, nation_data):
    try:
        cursor.execute("INSERT INTO nations (nation_name, nation_flag) VALUES (%s, %s)", (nation_data["name"], nation_data["flag_image"]))
        return cursor.lastrowid
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
    
def delete_source(cursor, source_id):
    cursor.execute("DELETE FROM sources WHERE source_id = %s", (source_id,))

def delete_transfer(cursor, transfer_id):
    query = """
    DELETE FROM source_transfer
    WHERE transfer_id = %s"""

    cursor.execute(query, (transfer_id,))

    query = """
    DELETE FROM transfers
    WHERE transfer_id = %s"""

    cursor.execute(query, (transfer_id,))
    
def delete_team(cursor, team_id):
    query = """
    DELETE FROM teams
    WHERE team_id = %s"""

    cursor.execute(query, (team_id,))
    
def bump_transfer(cursor, transfer_id):
    cur_time = int(time.time())
    query = "INSERT INTO sources (timestamp, source_type) VALUES (%s, 'official')"
    cursor.execute(query, (cur_time,))
    source_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO source_transfer (source_id, transfer_id) VALUES (%s, %s)", (source_id, transfer_id))
    