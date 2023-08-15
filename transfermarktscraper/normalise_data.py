from .scraper import parse_search_results, get_teams_from_search_results, get_players_from_search_results
import json
import re
from unidecode import unidecode

DIRECTORY = "transfermarktscraper/"
#DIRECTORY = ""

def check_replace_json(file_name, names):
    with open(DIRECTORY + file_name, "r") as f:
        json_data = json.load(f)
    new_names = []
    for name in names:
        if name.lower() in json_data:
            new_names.append(json_data[name.lower()])
        else:
            new_names.append(name)
    return new_names

def normalise_saudi_teams(team_names):
    for i in range(len(team_names)):
        split = team_names[i].split(" ")
        try:
            al = split.index("al")
            split[al+1] = "al-" + split[al+1]
            split.remove("al")
            team_names[i] = " ".join(split)
        except:
            pass
        
    return team_names

def remove_accents(names):
    return [unidecode(name) for name in names]

def normalise_fc(team_name):
    fc = re.compile(r"f.?c.?", re.IGNORECASE)
    team_name = re.sub(fc, "fc", team_name)
    return team_name

def remove_duplicates(names):
    sorted_names = sorted(names, key=len, reverse=True)
    
    for sorted_name in sorted_names:
        split = sorted_name.split(" ")
        if len(split) > 1:
            for i in range(len(split)):
                if split[i] in sorted_names:
                    names.remove(split[i])
    
    return names

def prepare_team_names(team_names):
    team_names = remove_accents(team_names)
    team_names = check_replace_json("team_names.json", team_names)
    team_names = check_and_handle_twitter_name(team_names)
    team_names = [name.lower() for name in team_names]
    team_names = remove_duplicates(team_names)
    team_names = [normalise_fc(team_name) for team_name in team_names]
    team_names = normalise_saudi_teams(team_names)
    return team_names

def prepare_player_names(player_names):
    player_names = remove_accents(player_names)
    player_names = check_and_handle_twitter_name(player_names)
    player_names = [name.lower() for name in player_names]
    player_names = remove_duplicates(player_names)
    return player_names

#TODO reduce cognitive complexity and make searching more robust by trying searching without fc, calcio, fussball etc.
def normalise_data(player_names, current_team_names, rumoured_team_names):
    player_names = prepare_player_names(player_names)
    
    current_team_names = prepare_team_names(current_team_names)
    
    rumoured_team_names = prepare_team_names(rumoured_team_names)
    
    rumoured_search_outputs = []
    for team_name in rumoured_team_names:
        try:
            team_search_output = get_teams_from_search_results(team_name)[0]
        except Exception as e:
            print(e)
            continue
        if team_search_output not in rumoured_search_outputs:
            rumoured_search_outputs.append(team_search_output)
            
    current_search_outputs = []
    for team_name in current_team_names:
        try:
            team_search_output = get_teams_from_search_results(team_name)[0]
        except:
            continue
        if team_search_output not in current_search_outputs:
            current_search_outputs.append(team_search_output)
            
    for current_team in current_search_outputs:
        if current_team in rumoured_search_outputs:
            current_search_outputs.remove(current_team)
    
    player_search_outputs = []
    for player_name in player_names:
        if "#" in player_name or "@" in player_name:
            player_name = handle_twitter_name(player_name)
        try:
            if current_search_outputs != []:
                player_search_output = get_players_from_search_results(player_name, current_search_outputs[0])[0]
            else:
                player_search_output = get_players_from_search_results(player_name)[0]
        except:
            continue
        if player_search_output not in player_search_outputs:
            player_search_outputs.append(player_search_output)
            
    
    player_searched_names = [player_search_output[0] for player_search_output in player_search_outputs]
    
    if len(player_searched_names) == 0:
        if len(current_search_outputs) != 0:
            print(current_search_outputs)
        raise Exception("No players found for " + str(player_names) + ".")
    elif len(rumoured_search_outputs) == 0:
        raise Exception("No rumoured teams found for " + str(rumoured_team_names) + ".")
        
    return player_searched_names, current_search_outputs, rumoured_search_outputs


def separate_words_by_re(expression, name):
    names = []
    index = re.finditer(expression, name)
    prev = 0
    for match in index:
        span_before = name[prev:match.start()]
        if span_before != "":
            names.append(span_before)
        names.append(match.group())
        prev = match.end()
    span_after = name[prev:]
    if span_after != "":
        names.append(span_after)
        
    return names
        
        
def check_and_handle_twitter_name(names):
    new_names = []
    for name in names:
        if "#" in name or "@" in name:
            name = handle_twitter_name(name)
        new_names.append(name)
    return new_names
        
#TODO improve
def handle_twitter_name(team_name):
    team_name = re.sub(r"[@#]", "", team_name)
    
    if len(team_name) <= 5:
        return team_name
    
    delimiter = r"[ _-]+"
    split_team_name = re.split(delimiter, team_name)
    split_team_name = [name for name in split_team_name if name != ""]
    
    new_team_name = []
    for split in split_team_name:
        names = separate_words_by_re(r"[A-Z][a-z]+", split)
        new_team_name.extend(names)
        
            
                    
    split_team_name = new_team_name
    
    with open(DIRECTORY + "common_addons.txt", "r") as f:
        common_addons = [line.strip() for line in f.readlines()]
    
    regex = "|".join(common_addons) + r"|\d+"
    regex = re.compile(regex, re.IGNORECASE)
    
    new_team_name = []
    for split in split_team_name:
        names = separate_words_by_re(regex, split)
        new_team_name.extend(names)
        
    return " ".join(new_team_name)
        
    
#print(handle_twitter_name("@BorussiaMGB_en"))

#print(normalise_data(['Ludwig Augustinsson'], ['Sevilla'], ['Anderlecht', 'Aston Villa']))
        
