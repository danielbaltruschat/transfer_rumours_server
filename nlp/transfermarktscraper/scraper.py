from bs4 import BeautifulSoup
import requests
import re
import json
import os

HEADERS = {"User-Agent": "Mozilla/5.0"}
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class Item:
    def __init__(self, name, url, item_type, team_url=None):
        self.name = name
        self.url = url
        self.item_type = item_type
        self.team_url = team_url

        

def parse_search_results(search, search_type):
    if search_type == "player":
        transfermarkt_text = "Search results for players"
    elif search_type == "team" or search_type == "nation":
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
    
    with open(os.path.join(CURRENT_PATH, "national_teams.json"), "r") as f:
        national_teams = json.load(f)
    
    national_teams = "|".join(national_teams)
    national_team_expression = re.compile(r"(" + national_teams + r")( U\d{1,2})?")
    
    if national_team_expression.match(search.lower()):
        raise Exception("Cannot get teams for national team " + search + ".")   
    
    all_results = parse_search_results(search, "team")
    
    teams = []

    for result in all_results:
        name = result.find("td", class_="hauptlink").find("a", href=True)
        link = name['href']
        name = name.get_text()
        market_value = result.findChild("td", class_="rechts").get_text()
        
        if market_value == "-":
            break
        
        #checks if team is not a national team
        if not national_team_expression.match(name.lower()):        
            teams.append(Item(name, link, "team"))
    
    if len(teams) == 0:
        raise Exception("No results found for " + search + ".")
        
    return teams

def get_players_from_search_results(player_name, team_name=None):
    all_players = parse_search_results(player_name, "player")
    
    players = []
    for player in all_players:
        #checks if market value is not zero
        if player.find("td", class_="rechts hauptlink").get_text() == "-":
            continue

        player_element = player.find("td", class_="hauptlink").find("a", href=True)
        player_link = player_element['href']
        player_name = player_element.get_text()
        team_element = player.find("td").find_all("td")[2].find("a")
        if team_element == None:
            continue
        team = team_element.get_text()
        team_link = team_element['href']
        
        #team_name may not exist so it is checked first
        if team_name == None or team_name.lower() in team.lower():
            if team_name != player_name:
                players.append(Item(player_name, player_link, "player", team_url=team_link))
            
    return players
    


def check_team_name(name_to_test, actual_team_name): #function to check the inputted team name against the team name listed on transfermarkt
    valid = True
    name_split = name_to_test.split(" ")
    for part in name_split:
        if part.lower() not in actual_team_name.lower():
            valid = False
            break
    return valid

def get_player_info_from_link(player_link):
    #Gets details from the player's page
    url = "https://www.transfermarkt.com" + player_link
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    main = soup.find("main")
    
    player_name = main.find("h1", class_="data-header__headline-wrapper")
    player_name = player_name.find("strong").previous_sibling + player_name.find("strong").get_text()
    player_name = player_name.strip()

    team = main.find("div", class_="data-header__club-info").find("a")
    team_name = team.get_text()
    team_link = team["href"]

    player_face_url = main.find("div", class_="data-header__profile-container").find("img")['src']

    if "default.jpg" in player_face_url:
        player_face_url = None
        
    general_info = main.find("div", class_="data-header__info-box").find("div")

    general_info = general_info.find_all("li")
    general_info_dict = {}
    for li in general_info:
        text = li.next_element.strip()[:-1]
        general_info_dict[text] = li

    nation_name = general_info_dict["Citizenship"].find("img")["title"]

    date_of_birth = general_info_dict["Date of birth/Age"].find("span").get_text()
    date_of_birth = normalise_dob(date_of_birth)

    position = general_info_dict["Position"].find("span").get_text().strip()

    market_value = main.find("div", class_="data-header__box--small").find("a")
    market_value = market_value.find_all("span")
    market_value = "".join([market_value[0].next_sibling, market_value[1].get_text()])


    return {"player_name": player_name, "team_name": team_name, "team_link": team_link, "player_face_url": player_face_url, "position": position, "market_value": market_value, "nation_name": nation_name, "player_link": player_link, "date_of_birth": date_of_birth}


def normalise_dob(date_of_birth): #returns date as string in format YEAR-MONTH-DAY
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date_of_birth = re.sub(r"\(\d*\)", "", date_of_birth)
    date_of_birth = date_of_birth.strip()
    date_of_birth = date_of_birth.replace(",", "")
    date_of_birth = date_of_birth.split(" ")
    month = str(months.index(date_of_birth[0]) + 1)
    day = date_of_birth[1]
    year = date_of_birth[2]
    return "-".join([year, month, day])

def get_team_info_from_link(team_link):
    try:
    #Gets details from the player's page
        url = "https://www.transfermarkt.com" + team_link
        page = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        main = soup.find("main")
        team_name = main.find("h1").get_text().strip()
        
        league_name = main.find("div", class_="data-header__club-info").find("a").get_text().strip()
        
        team_logo_url = main.find("div", class_="data-header__profile-container").find("img")['src']

    except Exception as e:
        print(e)
        raise Exception("Error retrieving data for team: ", team_link)

    return {"team_name": team_name, "league_name": league_name, "team_logo_url": team_logo_url, "team_link": team_link}
    

def get_player_info(player_name, team_name=None): #Gets the player's name, team and face image url from the search results
    player = get_players_from_search_results(player_name, team_name)[0]

    return get_player_info_from_link(player.url)



def get_team_info(team_name): #Gets the team's name, league and logo image url from the search results, similar structure to get_player_info but slightly different format in transfermarkt   
    team = get_teams_from_search_results(team_name)[0]
        
    return get_team_info_from_link(team.url)

def get_nation_info(nation_name):
    all_nations = parse_search_results(nation_name, "nation")
    
    nation_name_link = all_nations[0].find("td", class_="hauptlink").find("a", href=True)
    link = nation_name_link['href']
    nation_link = link
    nation_name = nation_name_link.get_text()
        
    if nation_link == None:
        raise Exception("No team found", nation_name)

    #Gets details from the player's page
    url = "https://www.transfermarkt.com" + nation_link
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    main = soup.find("main")
    nation_flag_url = main.find("div", class_="data-header__profile-container").find("img")['src']

    return {"name": nation_name, "flag_image": nation_flag_url}


# info = get_team_info_from_link("/statistik/vertragslosespieler")
#print(get_teams_from_search_results("nigeria u18"))
# pass
# print(get_player_info("Jamal Musiala"))
# print(get_team_info("Bayern"))

# items = get_teams_from_search_results("Borussia")
# for item in items:
#     print("Item:", item, "Item.name:", item.name)