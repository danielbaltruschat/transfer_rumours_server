import json
import spacy
from spacy.tokens import DocBin, Doc
import re
from langdetect import detect
import dl_translate as dlt

if not Doc.has_extension("rel"):
    Doc.set_extension("rel", default={})
    
if not Doc.has_extension("resolved"):
    Doc.set_extension("resolved", default={})

nlp = spacy.blank("en")

def open_json(json_file):
    with open(json_file, encoding="utf-8") as file:
        data = json.load(file)
    return data
        
        

def get_char_spans(text, entities, index):
    all_spans = []
    for entity in entities:
        spans = find_non_overlapping_occurences(entity[index], text)
        for span in spans:
            if span not in all_spans:
                all_spans.append(span)
    return all_spans
        

def find_non_overlapping_occurences(patterns, text):
    if len(patterns) == 0:
        return []
    pattern = re.compile('|'.join(patterns))
    matches = pattern.finditer(text)
    matches_list = [[matches.start(), matches.end()] for matches in matches]
    if len(matches_list) == 0:
        raise ValueError("No matches found", patterns, text)
    return matches_list


def remove_invisible_chars(input_string):
    # Define a regular expression to match invisible characters
    invisible_char_pattern = re.compile(r'[\uFE0F\u200B]+')
    
    # Remove all occurrences of invisible characters
    cleaned_string = invisible_char_pattern.sub('', input_string)
    
    return cleaned_string



def entity_annotation(doc, tweet):    
    relation_instances = get_relations_string(tweet)
    ent_strings = {}
    ent_strings["players"], ent_strings["teams"] = get_players_and_teams_from_instances(relation_instances)

    for i in range(len(tweet["all_players"])):
        player = tweet["all_players"][i]
        player_added = False
        for list_strings in ent_strings["players"]:
            if player in list_strings:
                player_added = True
                break
        if not player_added:
            ent_strings["players"].append([player])

    for i in range(len(tweet["all_teams"])):
        team = tweet["all_teams"][i]
        team_added = False
        for list_strings in ent_strings["teams"]:
            if team in list_strings:
                team_added = True
                break
        if not team_added:
            ent_strings["teams"].append([team])
    

    text_to_ent_dict = ([],[])
    
    
    for label in ent_strings.keys():
        for players_or_teams in ent_strings[label]:
            ents = []
            spans = find_non_overlapping_occurences(players_or_teams, doc.text) 
            for span in spans:
                start = doc.text[span[0]]
                end = doc.text[span[1]-1]
                spacy_span = doc.char_span(span[0], span[1], label=label[:-1].upper())
                try:
                    doc.ents = list(doc.ents) + [spacy_span]
                    ents.append(spacy_span)
                except:
                    #usually failures are when the string is inside a # or @
                    print("Error with entity annotation", start, end, span, doc.text)
            text_to_ent_dict[0].append(players_or_teams)
            text_to_ent_dict[1].append(ents)
              
    new_instances = get_relations_ent(relation_instances, text_to_ent_dict)
    ents_grouped = get_players_and_teams_from_instances(new_instances)
    doc = modify_doc_for_entity_resolution(doc, ents_grouped[0], ents_grouped[1])
    doc = modify_doc_relations(doc, new_instances)    
      
    return doc

def get_players_and_teams_from_instances(instances):
    players, teams = [], []
    for instance in instances:
        if instance[0] not in players:
            players.append(instance[0])
        if instance[1] not in teams:
            teams.append(instance[1])
            
    return players, teams

def get_relations_string(tweet):
    instances_string = []
        
    for transfer in tweet["transfers"]:

        player = transfer["involved_players"]
        if len(transfer["current_teams"]) != 0:
            if (player, transfer["current_teams"], "plays_for") not in instances_string:
                instances_string.append((player, transfer["current_teams"], "plays_for"))
        if len(transfer["rumoured_teams"]) != 0:
            #ignores teams which are confirmed to no longer be rumoured with the player
            if transfer["stage"] == "deal_off":
                if (player, transfer["rumoured_teams"], "none") not in instances_string:
                    instances_string.append((player, transfer["rumoured_teams"], "none"))
            else:
                if (player, transfer["rumoured_teams"], "rumoured_to_join") not in instances_string:
                    instances_string.append((player, transfer["rumoured_teams"], "rumoured_to_join"))
        else:
            instances_string.append((player, [], "none"))
        
                
    return instances_string

def get_relations_ent(instances_string, text_to_ent_dict):
    new_instances = []
    for instance in instances_string:
        if instance[2] != "none":
            new_instance = [text_to_ent_dict[1][text_to_ent_dict[0].index(instance[0])], text_to_ent_dict[1][text_to_ent_dict[0].index(instance[1])], instance[2]]
            new_instances.append(new_instance)

    return new_instances
    
def modify_doc_relations(doc, instances_ent): 
    player_ents = [ent for ent in doc.ents if ent.label_ == "PLAYER"]
    team_ents = [ent for ent in doc.ents if ent.label_ == "TEAM"]
    
    for player_ent in player_ents:
        for team_ent in team_ents:
            offset = (player_ent.start, team_ent.start)
            if offset not in doc._.rel:
                doc._.rel[offset] = {"plays_for": 0.0, "rumoured_to_join": 0.0}
        
         
    for instance in instances_ent:
        for player_ent in instance[0]:
            for team_ent in instance[1]:
                offset = (player_ent.start, team_ent.start)
                if instance[2] != "none":
                    doc._.rel[offset][instance[2]] = 1.0
    
    return doc

def modify_doc_for_entity_resolution(doc, player_ents_grouped, team_ents_grouped):
    player_ents = [ent for ent in doc.ents if ent.label_ == "PLAYER"]
    team_ents = [ent for ent in doc.ents if ent.label_ == "TEAM"]
    
    for i in range(len(player_ents)):
        for ent in player_ents[i+1:]:
            offset = (player_ents[i].start, ent.start)
            doc._.resolved[offset] = 0.0
            
    for i in range(len(team_ents)):
        for ent in team_ents[i+1:]:
            offset = (team_ents[i].start, ent.start)
            doc._.resolved[offset] = 0.0
    
    for ent_groups in [player_ents_grouped, team_ents_grouped]:
        for ent_group in ent_groups:
            for i, ent1 in enumerate(ent_group[:-1]):
                for ent2 in ent_group[i+1:]:
                    offset = (ent1.start, ent2.start)
                    doc._.resolved[offset] = 1.0
    return doc
            

def get_ents_with_text(doc, text):
    ents = []
    for ent in doc.ents:
        if ent.text == text:
            ents.append(ent)
    return ents        
    


def annotation_from_list(data):
    db = DocBin(store_user_data=True)
    for tweet in data:
        cleaned_text = remove_invisible_chars(tweet["text"])
        doc = nlp(cleaned_text)
        doc = entity_annotation(doc, tweet)
        db.add(doc)
    return db


def get_iob_formatted_from_doc(doc):
    formatted = []
    for token in doc:
        if token.ent_iob_ != "O":
            formatted.append(token.text + " " + token.ent_iob_ + "-" +  token.ent_type_)
        else:
            formatted.append(token.text + " " + token.ent_iob_)
    return formatted


data = [
    {
        "text": "Mikel Arteta on Thomas Partey: \"Part of my plans? Of course, without a question of a doubt. Thomas is a super important player for us and for me\". 🔴⚪️\n\n\"I want him to be part of the team\".",
        "is_rumour": False,
        "all_players": ["Thomas Partey", "Thomas"],
        "all_teams": [],
        "transfers": [
            {
                "involved_players": ["Thomas Partey", "Thomas"],
                "current_teams": [],
                "rumoured_teams": [],
                "bid_fees": [],
                "stage": "deal_off"
            }
        ]
    },
    {
        "text": "❗️BREAKING EXCL. NEWS #Kane: Got the info that his move to FC Bayern is „looking more likely now“ !!!\n\n➡️ As reported: Bayern bosses, Tottenham and Kane‘s management were in very good and respectful negotiations today and tonight. \n\n❗️NOW the deal is on verge to be sealed as KANE WANTS TO JOIN BAYERN! \n\n@SkySportDE\n 🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "is_rumour": True,
        "all_players": ["#Kane", "Kane's", "KANE"],
        "all_teams": ["FC Bayern", "Tottenham", "BAYERN", "Bayern"],
        "transfers": [
            {
                "involved_players": ["#Kane", "Kane's", "KANE"],
                "current_teams": ["Tottenham"],
                "rumoured_teams": ["FC Bayern", "BAYERN", "Bayern"],
                "bid_fees": [],
                "stage": "full_agreement"
            }
        ]
    }
]

data2 = open_json("../tweets.json")
db = annotation_from_list(data2)
db.to_disk("./tweets.spacy")   