from .transfermarktscraper.scraper import parse_search_results, get_teams_from_search_results, get_players_from_search_results
import json
import re
import os
from unidecode import unidecode
from spacy.language import Language

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


def prepare_team_names(team_names):
    team_names = remove_accents(team_names)
    team_names = check_replace_json("team_names.json", team_names)
    team_names = check_and_handle_twitter_name(team_names)
    team_names = [name.lower() for name in team_names]
    team_names = [normalise_fc(team_name) for team_name in team_names]
    team_names = normalise_saudi_teams(team_names)
    team_names = sorted(team_names, key=len, reverse=True)
    return team_names

def prepare_player_names(player_names):
    player_names = remove_accents(player_names)
    player_names = check_and_handle_twitter_name(player_names)
    player_names = [name.lower() for name in player_names]
    player_names = sorted(player_names, key=len, reverse=True)
    return player_names

#link is a better unique identifier than the name
def check_link_in_list_of_items(link, items):
    for i in range(len(items)):
        if items[i].url == link:
            return True
    return False
    
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

    #these two lists are parallel
    search_outputs_items = []
    search_outputs_links = []
    for name in names:
        try:
            #[0] takes top result in transfermarkt search
            if current_team_name == None:
                search_output = func(name)[0]
            else:
                search_output = func(name, current_team_name)[0]
        except Exception as e:
            print(e)
            continue
        search_outputs_items.append(search_output)
        search_outputs_links.append(search_output.url)
    
    
    
    if len(search_outputs_items) == 0:
        return -1
    
    if len(search_outputs_items) == 1:
        return search_outputs_items[0]
    else:
        freqencies = {}
        for link in search_outputs_links:
            if link in freqencies:
                freqencies[link] += 1
            else:
                freqencies[link] = 1
                
        highest_frequency = 0
        link_with_highest_frequency = ""
        for link, frequency in freqencies.items():
            if frequency > highest_frequency:
                highest_frequency = frequency
                link_with_highest_frequency = link
        
        i = search_outputs_links.index(link_with_highest_frequency)
        return search_outputs_items[i]
    
    


def separate_string_by_re(expression, name):
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
        names = separate_string_by_re(r"[A-Z][a-z]+", split)
        new_team_name.extend(names)
        
            
                    
    split_team_name = new_team_name
    
    with open(os.path.join(DIRECTORY, "common_addons.txt"), "r") as f:
        common_addons = [line.strip() for line in f.readlines()]
    
    regex = "|".join(common_addons) + r"|\d+"
    regex = re.compile(regex, re.IGNORECASE)
    
    new_team_name = []
    for split in split_team_name:
        names = separate_string_by_re(regex, split)
        new_team_name.extend(names)
        
    def remove_all_occurrences_of_item_from_list(item, list_):
        return [name for name in list_ if name.lower() != item.lower()]
    
    addons = ["en", "official"]
    for addon in addons:
        new_team_name = remove_all_occurrences_of_item_from_list(addon, new_team_name)
        
    return " ".join(new_team_name)
        
@Language.component("normalise_groups")
def normalise_groups(doc):
    #get all indexes involved
    indexes_involved = [item for tuple_ in doc._.transfers.keys() for item in tuple_]
    player_indexes = []
    doc._.normalised_names = [-1 for _ in range(len(doc._.ent_groups))]
    for i, group in enumerate(doc._.ent_groups):
        if i in indexes_involved:
            ent = doc._.ent_start_dict[group[0]]
            if ent.label_ == "PLAYER":
                player_indexes.append(i)
            else:
                #this code runs if the ent's label is 'TEAM'
                name_group = [doc._.ent_start_dict[ent_start].text for ent_start in group] #get list of strings from list of ent_starts
                normalised = normalise_names(name_group, "team") #returns an instance of Item class defined in scraper.py
                doc._.normalised_names[i] = normalised
        
    def find_current_team_for_player(transfers, index):
        for key, relation in transfers.items():
            if relation == "plays_for":
                if key[0] == index:
                    return key[1]
                elif key[1] == index:
                    return key[0]
        return None

    def find_uncertain_teams_for_player(transfers, index):
        uncertain_team_keys = []
        for key, relation in transfers.items():
            if relation == "uncertain":
                if key[0] == index:
                    uncertain_team_keys.append(key[1])
                elif key[1] == index:
                    uncertain_team_keys.append(key[0])
        return uncertain_team_keys
            
    """
    TRY CURRENT_TEAM
    TRY RUMOURED_TEAM
    TRY PLAYER without
    """

    for player_index in player_indexes:
        current_team_index = find_current_team_for_player(doc._.transfers, player_index)
        uncertain_teams_indexes = find_uncertain_teams_for_player(doc._.transfers, player_index)
        
        group = doc._.ent_groups[player_index]
        name_group = [doc._.ent_start_dict[ent_start].text for ent_start in group] 
        
        if current_team_index == None or doc._.normalised_names[current_team_index] == -1:
            normalised = normalise_names(name_group, "player")
            if len(uncertain_teams_indexes) >= 2:
                for i, item in enumerate(doc._.normalised_names):
                    if item != -1 and item.url == normalised.team_url:
                        doc._.transfers[(player_index, i)] = "plays_for"
                
                for team_index in uncertain_teams_indexes:
                    if doc._.transfers[(player_index, team_index)] != "plays_for":
                        doc._.transfers[(player_index, team_index)] = "rumoured_to_join"
                      
        else:
            current_team_name = doc._.normalised_names[current_team_index].name
            normalised = normalise_names(name_group, "player", current_team_name=current_team_name)

            if len(uncertain_teams_indexes) != 0:
                for uncertain_team_index in uncertain_teams_indexes:
                    doc._.transfers[(player_index, uncertain_team_index)] = "rumoured_to_join"
            
        doc._.normalised_names[player_index] = normalised
        
    return doc
    
    
#print(normalise_fc("fc lorient"))

#print(normalise_data(['Ludwig Augustinsson'], ['Sevilla'], ['Anderlecht', 'Aston Villa']))

        
