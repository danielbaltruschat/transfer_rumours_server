from .transfermarktscraper.scraper import parse_search_results, get_teams_from_search_results, get_players_from_search_results
import json
import re
import os
from unidecode import unidecode

DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def check_replace_json(file_name, names):
    with open(os.path.join(DIRECTORY, file_name), "r") as f:
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
    fc = re.compile(r"f\.?c\.?", re.IGNORECASE)
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
    #team_names = check_replace_json("team_names.json", team_names)
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

#link is a better unique identifier than the name
def check_link_in_list_of_items(link, items):
    for i in range(len(items)):
        if items[i].url == link:
            return True
    return False
    
#TODO use majority voting system
def normalise_names(names, player_or_team, current_team_name=None):
    if player_or_team == "team":
        if current_team_name != None:
            raise Exception("Current team has been specified when the mode is not 'player'")
        names = prepare_team_names(names)
        func = get_teams_from_search_results
    elif player_or_team == "player":
        names = prepare_player_names(names)
        func = get_players_from_search_results
    else:
        raise Exception("Second argument 'player_or_team' should be 'player' or 'team'.")
    

    search_outputs = []
    for name in names:
        try:
            #[0] takes first result in transfermarkt search
            if current_team_name == None:
                search_output = func(name)[0]
            else:
                search_output = func(name, current_team_name)[0]
        except Exception as e:
            print(e)
            continue
        if not check_link_in_list_of_items(search_output.url, search_outputs):
            search_outputs.append(search_output)
            
    if len(search_outputs) == 0:
        return -1
    
    return search_outputs[0]
    


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
    
    with open(os.path.join(DIRECTORY, "common_addons.txt"), "r") as f:
        common_addons = [line.strip() for line in f.readlines()]
    
    regex = "|".join(common_addons) + r"|\d+"
    regex = re.compile(regex, re.IGNORECASE)
    
    new_team_name = []
    for split in split_team_name:
        names = separate_words_by_re(regex, split)
        new_team_name.extend(names)
        
    def remove_all_occurrences_of_item_from_list(item, list_):
        return [name for name in list_ if name.lower() != item.lower()]
    
    addons = ["en", "official"]
    for addon in addons:
        new_team_name = remove_all_occurrences_of_item_from_list(addon, new_team_name)
        
    return " ".join(new_team_name)
        
    
#print(normalise_fc("fc lorient"))

#print(normalise_data(['Ludwig Augustinsson'], ['Sevilla'], ['Anderlecht', 'Aston Villa']))
        
