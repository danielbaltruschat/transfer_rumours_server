from flask import Flask, jsonify
import os
import MySQLdb


app = Flask(__name__)

mysql_user = os.environ['MYSQL_USER'].strip()
mysql_password = os.environ['MYSQL_PASSWORD'].strip()
mysql_port = int(os.environ['MYSQL_PORT'].strip())

print(mysql_user, mysql_password)

try:
    connection_pool = MySQLdb.connect(host="mysql", user=mysql_user, passwd=mysql_password, port=mysql_port, db="transfer_data")
except:
    raise Exception("Could not connect to database")

OK_STATUS_CODE = 200
BAD_REQUEST_STATUS_CODE = 500

#Gets all the transfers from the database
@app.route('/all_transfers', methods=['GET'])
def get_all_transfers():
    try:
        cursor = connection_pool.cursor()
        
        query = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers
        JOIN
            players ON transfers.player_id = players.player_id
        JOIN
            teams current_team ON players.current_team_id = current_team.team_id
        JOIN
            teams rumoured_team ON transfers.rumoured_team_id = rumoured_team.team_id
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
        '''
        
        query2 = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers, players, teams AS current_team, teams AS rumoured_team,
            (SELECT transfer_id, MAX(timestamp) AS latest_timestamp
            FROM sources, source_transfer
            WHERE sources.source_id = source_transfer.source_id
            GROUP BY transfer_id) AS latest_sources
        WHERE
            transfers.player_id = players.player_id
            AND players.current_team_id = current_team.team_id
            AND transfers.rumoured_team_id = rumoured_team.team_id
            AND transfers.transfer_id = latest_sources.transfer_id
        '''
        
        cursor.execute(query)
        all_transfers = cursor.fetchall()
        
        formatted_transfers = []
        for transfer in all_transfers:
            transfer_dict = {
                'transfer_id': transfer[0],
                'player_name': transfer[1],
                'player_image': transfer[2],
                'current_team_name': transfer[3],
                'current_team_logo': transfer[4],
                'rumoured_team_name': transfer[5],
                'rumoured_team_logo': transfer[6],
                'latest_timestamp': transfer[7]
                }
            formatted_transfers.append(transfer_dict)
        
        
        cursor.close()
        
        return jsonify(formatted_transfers), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve all transfers'}), BAD_REQUEST_STATUS_CODE
    
@app.route('/transfer_by_id/<int:transfer_id>', methods=['GET'])
def get_transfer_by_id(transfer_id):
    try:
        cursor = connection_pool.cursor()
        
        query = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers
        JOIN
            players ON transfers.player_id = players.player_id
        JOIN
            teams current_team ON players.current_team_id = current_team.team_id
        JOIN
            teams rumoured_team ON transfers.rumoured_team_id = rumoured_team.team_id
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
        WHERE
            transfers.transfer_id = %s
        '''
        
        query2 = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers, players, teams AS current_team, teams AS rumoured_team,
            (SELECT transfer_id, MAX(timestamp) AS latest_timestamp
            FROM sources, source_transfer
            WHERE sources.source_id = source_transfer.source_id
            GROUP BY transfer_id) AS latest_sources
        WHERE
            transfers.player_id = players.player_id
            AND players.current_team_id = current_team.team_id
            AND transfers.rumoured_team_id = rumoured_team.team_id
            AND transfers.transfer_id = latest_sources.transfer_id
            AND transfers.transfer_id = %s
        '''
        
        cursor.execute(query, (transfer_id,))
        all_transfers = cursor.fetchall()
        
        formatted_transfers = []
        for transfer in all_transfers:
            transfer_dict = {
                'transfer_id': transfer[0],
                'player_name': transfer[1],
                'player_image': transfer[2],
                'current_team_name': transfer[3],
                'current_team_logo': transfer[4],
                'rumoured_team_name': transfer[5],
                'rumoured_team_logo': transfer[6],
                'latest_timestamp': transfer[7]
                }
            formatted_transfers.append(transfer_dict)
        
        
        cursor.close()
        
        return jsonify(formatted_transfers), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve transfer with id {0}'.format(transfer_id)}), BAD_REQUEST_STATUS_CODE
    
@app.route('/transfer_by_player_id/<int:player_id>', methods=['GET'])
def get_transfer_by_player_id(player_id):
    try:
        cursor = connection_pool.cursor()
        #Parameterized query to prevent SQL injection
        query = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers
        JOIN
            players ON transfers.player_id = players.player_id
        JOIN
            teams current_team ON players.current_team_id = current_team.team_id
        JOIN
            teams rumoured_team ON transfers.rumoured_team_id = rumoured_team.team_id
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
        WHERE
            players.player_id = %s
        '''
        
        query2 = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers, players, teams AS current_team, teams AS rumoured_team,
            (SELECT transfer_id, MAX(timestamp) AS latest_timestamp
            FROM sources, source_transfer
            WHERE sources.source_id = source_transfer.source_id
            GROUP BY transfer_id) AS latest_sources
        WHERE
            transfers.player_id = players.player_id
            AND players.current_team_id = current_team.team_id
            AND transfers.rumoured_team_id = rumoured_team.team_id
            AND transfers.transfer_id = latest_sources.transfer_id
            AND players.player_id = %s
        '''
        
        cursor.execute(query, (player_id,))
        all_transfers = cursor.fetchall()
        
        formatted_transfers = []
        for transfer in all_transfers:
            transfer_dict = {
                'transfer_id': transfer[0],
                'player_name': transfer[1],
                'player_image': transfer[2],
                'current_team_name': transfer[3],
                'current_team_logo': transfer[4],
                'rumoured_team_name': transfer[5],
                'rumoured_team_logo': transfer[6],
                'latest_timestamp': transfer[7]
                }
            formatted_transfers.append(transfer_dict)
        
        
        cursor.close()
        
        return jsonify(formatted_transfers), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve transfers for player with id {0}'.format(player_id)}), BAD_REQUEST_STATUS_CODE
        
@app.route('/transfer_by_team_id/<int:team_id>', methods=['GET'])
def get_transfer_by_team_id(team_id):
    try:
        cursor = connection_pool.cursor()
        #Parameterized query to prevent SQL injection
        query = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers
        JOIN
            players ON transfers.player_id = players.player_id
        JOIN
            teams current_team ON players.current_team_id = current_team.team_id
        JOIN
            teams rumoured_team ON transfers.rumoured_team_id = rumoured_team.team_id
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
        WHERE
            transfers.rumoured_team_id = %s OR players.current_team_id = %s
        '''
        
        query2 = '''SELECT
            transfers.transfer_id,
            player_name,
            player_image,
            current_team.team_name AS current_team_name,
            current_team.logo_image AS current_team_logo,
            current_team.league_name AS current_team_league_name,
            rumoured_team.team_name AS rumoured_team_name,
            rumoured_team.logo_image AS rumoured_team_logo,
            rumoured_team.league_name AS rumoured_team_league_name,
            latest_sources.latest_timestamp AS latest_timestamp
        FROM
            transfers, players, teams AS current_team, teams AS rumoured_team,
            (SELECT transfer_id, MAX(timestamp) AS latest_timestamp
            FROM sources, source_transfer
            WHERE sources.source_id = source_transfer.source_id
            GROUP BY transfer_id) AS latest_sources
        WHERE
            transfers.player_id = players.player_id
            AND players.current_team_id = current_team.team_id
            AND transfers.rumoured_team_id = rumoured_team.team_id
            AND transfers.transfer_id = latest_sources.transfer_id
            AND (transfers.rumoured_team_id = %s OR players.current_team_id = %s)
        '''
        
        cursor.execute(query, (team_id,))
        all_transfers = cursor.fetchall()
        
        formatted_transfers = []
        for transfer in all_transfers:
            transfer_dict = {
                'transfer_id': transfer[0],
                'player_name': transfer[1],
                'player_image': transfer[2],
                'current_team_name': transfer[3],
                'current_team_logo': transfer[4],
                'rumoured_team_name': transfer[5],
                'rumoured_team_logo': transfer[6],
                'latest_timestamp': transfer[7]
                }
            formatted_transfers.append(transfer_dict)
        
        
        cursor.close()
        
        return jsonify(formatted_transfers), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve transfers for team with id {0}'.format(team_id)}), BAD_REQUEST_STATUS_CODE
    
@app.route('/search_players/<player_name>', methods=['GET'])
def search_players(player_name):
    try:
        cursor = connection_pool.cursor()
        
        #Parameterized query to prevent SQL injection
        query = """SELECT 
            player_id,
            player_name,
            player_image,
            team_id AS current_team_id,
            team_name AS current_team_name,
            logo_image AS current_team_logo
        FROM
            players
        JOIN
            teams ON players.current_team_id = teams.team_id
        WHERE
            player_name LIKE %s
        """
        query2 = """SELECT
            player_id,
            player_name,
            player_image,
            team_id AS current_team_id,
            team_name AS current_team_name,
            logo_image AS current_team_logo
        FROM
            players, teams
        WHERE
            players.current_team_id = teams.team_id
            AND LOWER(player_name) LIKE LOWER(%s)
        """
        cursor.execute(query, (player_name,))
        
        players = cursor.fetchall()
        
        formatted_players = []
        for player in players:
            player_dict = {
                'player_id': player[0],
                'player_name': player[1],
                "player_image": player[2],
                'current_team_id': player[3],
                'current_team_name': player[4],
                'current_team_logo': player[5]
                }
            formatted_players.append(player_dict)
        
        cursor.close()
        
        return jsonify(formatted_players), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve players with name {0}'.format(player_name)}), BAD_REQUEST_STATUS_CODE

@app.route('/search_teams/<team_name>', methods=['GET'])
def search_teams(team_name):
    try:
        cursor = connection_pool.cursor()
        
        #Parameterized query to prevent SQL injection
        query = """SELECT
            team_id,
            team_name,
            logo_image,
            league_name
        FROM
            teams
        WHERE
            team_name LIKE %s
        """
        query2 = """SELECT
            team_id,
            team_name,
            logo_image,
            league_name
        FROM
            teams
        WHERE
            LOWER(team_name) LIKE LOWER(%s)
        """
        cursor.execute(query, (team_name,))
        
        teams = cursor.fetchall()
        
        formatted_teams = []
        for team in teams:
            team_dict = {
                'team_id': team[0],
                'team_name': team[1],
                'logo_image': team[2],
                'league_name': team[3]
                }
            formatted_teams.append(team_dict)
        
        
        cursor.close()
        
        return jsonify(formatted_teams), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve teams with name {0}'.format(team_name)}), BAD_REQUEST_STATUS_CODE
        


@app.route('/get_sources_by_transfer_id/<int:transfer_id>', methods=['GET'])
def get_sources_by_transfer_id(transfer_id):
    try:
        cursor = connection_pool.cursor()
        
        #Parameterized query to prevent SQL injection
        query = """SELECT source_type, source_link, text, timestamp, author_name 
        FROM sources 
        JOIN source_transfer ON sources.source_id = source_transfer.source_id
        WHERE transfer_id = %s"""
        query2 = """SELECT source_type, source_link, text, timestamp, author_name
        FROM sources, source_transfer
        WHERE sources.source_id = source_transfer.source_id
        AND transfer_id = %s"""
        cursor.execute(query, (transfer_id,))
        
        sources = cursor.fetchall()
        
        formatted_sources = []
        for source in sources:
            source_dict = {
                'source_type': source[0],
                'source_link': source[1],
                "text": source[2],
                'timestamp': source[3],
                'author_name': source[4]
                }
            formatted_sources.append(source_dict)
        
        cursor.close()
        
        return jsonify(formatted_sources), OK_STATUS_CODE
    
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while trying to retrieve sources for transfer with id {0}'.format(transfer_id)}), BAD_REQUEST_STATUS_CODE

    