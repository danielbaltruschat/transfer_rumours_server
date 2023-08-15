from bs4 import BeautifulSoup
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse_search_results(search, search_type):
    if search_type == "player":
        transfermarkt_text = "Search results for players"
    elif search_type == "team":
        transfermarkt_text = "Search results: Clubs"
    else:
        raise ValueError("Invalid search type - should be 'player' or 'team'")
    
    url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query=" + search + "&x=0&y=0"


    #Get the page
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')

    rows = soup.find_all("div", class_="row")
    found_row = False
    i = 0
    while not found_row and i < len(rows):
        if rows[i].find("h2").get_text().startswith(transfermarkt_text):
            found_row = True
            row = rows[i]
        else:
            i += 1
        
    #For some reason the it goes to yw3 after yw1 so this fixes that
    # if i > 1:
    #     i += 1
        
    if not found_row:
        raise Exception("No results found for " + search + ".")

    #yw0 is the id of the table that contains the player data
    results = row.find(id="yw" + str(i))

    #Data is stored in odd and even rows so this gets all the rows and combines the odds and evens in order (they are in order of popularity)
    odd_results = results.find_all("tr", class_="odd")
    even_results = results.find_all("tr", class_="even")
    
    all_results = []
    for i in range(len(even_results)):
        all_results.append(odd_results[i])
        all_results.append(even_results[i])
    if len(odd_results) > len(even_results):
        all_results.append(odd_results[-1])

    if len(all_results) == 0:
        raise Exception("No results found for " + search + ".")
    
    return all_results

def get_teams_from_search_results(search):
    all_results = parse_search_results(search, "team")
    
    names = []

    for result in all_results:
        name = result.find("td", class_="hauptlink").find("a", href=True).get_text()
        names.append(name)
    
    return names

def get_players_from_search_results(player_name, team_name=None):
    all_players = parse_search_results(player_name, "player")
    
    player_names = []
    team_names = []
    for player in all_players:
        player_name = player.find("td", class_="hauptlink").find("a", href=True).get_text()
        team = player.find("td").find_all("a")[-1].get_text()
        #team_name may not exist so it is checked first
        if team_name == None or team_name.lower() in team.lower():
            player_names.append(player_name)
            team_names.append(team)
            
    return [player_and_team for player_and_team in zip(player_names, team_names)]
    


def check_team_name(name_to_test, actual_team_name): #function to check the inputted team name against the team name listed on transfermarkt
    valid = True
    name_split = name_to_test.split(" ")
    for part in name_split:
        if part.lower() not in actual_team_name.lower():
            valid = False
            break
    return valid

def get_player_info(player_name, team_name=None): #Gets the player's name, team and face image url from the search results
    all_players = parse_search_results(player_name, "player")

    player_link = None

    for player in all_players:
        player_name_link = player.find("td", class_="hauptlink").find("a", href=True)
        link = player_name_link['href']
        team = player.find("td").find_all("a")[-1].get_text()
        #team_name may not exist so it is checked first
        if team_name == None or team_name.lower() in team.lower():
            player_link = link
            player_name = player_name_link.get_text()
            team_name = team
            break

    if player_link == None:
        raise Exception("No player found", player_name, team_name)


    #Gets details from the player's page
    url = "https://www.transfermarkt.com" + player_link
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    main = soup.find("main")
    #header_logo = main.find("header", class_="data-header").find("div", class_="data-header__box--big")

    #team_logo = header_logo.find("a").find("img")

    # try:
    #     #regular expression that has http or https followed by any number of characters that are not spaces
    #     team_logo_url = re.findall(r'(https?://[^\s]+)', team_logo['srcset'])[1]
    # except:
    #     team_logo_url = team_logo['src']

    player_face_url = main.find("div", class_="data-header__profile-container").find("img")['src']

    if "default.jpg" in player_face_url:
        player_face_url = None

    return player_name, team_name, player_face_url



def get_team_info(team_name, league_name=None): #Gets the team's name, league and logo image url from the search results, similar structure to get_player_info but slightly different format in transfermarkt
    if team_name == "Without Club":
        return team_name, None, None
    
    all_teams = parse_search_results(team_name, "team")
    
    team_link = None
    for team in all_teams:
        team_name_link = team.find("td", class_="hauptlink").find("a", href=True)
        link = team_name_link['href']
        league = team.find("table", class_="inline-table").find_all("a")[-1].get_text()
        #league_name may not exist so it is checked first
        if league_name == None or (league_name.lower() in league.lower()):
            team_link = link
            team_name = team_name_link.get_text()
            league_name = league
            break
        
    if team_link == None:
        raise Exception("No team found", team_name, league_name)

    #Gets details from the player's page
    url = "https://www.transfermarkt.com" + team_link
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    main = soup.find("main")
    team_logo_url = main.find("div", class_="data-header__profile-container").find("img")['src']
    
    return team_name, league_name, team_logo_url

# print(get_players_from_search_results("Jamal"))
# print(get_teams_from_search_results("bayern"))