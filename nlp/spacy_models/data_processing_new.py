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

def augment_data(data):
    new_data = []
    mt = dlt.TranslationModel.load_obj("translation_model")
    for tweet in data:
        text = tweet["text"]
        try:
            #language_current = detect(text)
            language_current = "en"
        except:
            raise Exception("Error with language detection", text)
        target_languages = ["German"]
        for language in target_languages:
            if language != language_current:
                translated_text = language_translate_for_augmentation(mt, text, language_current, language)
                new_data.append({
                    "text": translated_text,
                    "is_rumour": tweet["is_rumour"],
                    "all_players": tweet["all_players"],
                    "all_teams": tweet["all_teams"],
                    "transfers": tweet["transfers"]
                })
    return new_data + data
        
        
        
def language_translate_for_augmentation(translator, text, original_language, target_language):
    # translator_forward = Translator(from_lang=original_language, to_lang=target_language)
    # translated = translator_forward.translate(text)
    translated = translator.translate(text, source=original_language, target=target_language)
    
    # translator_back = Translator(from_lang=target_language, to_lang=original_language)
    # translated_back = translator_back.translate(translated)
    translated_back = translator.translate(translated, source=target_language, target=original_language)
    
    return translated_back
        
        

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
    #print(matches_list)
    if len(matches_list) == 0:
        raise ValueError("No matches found", patterns, text)
    return matches_list


def remove_invisible_chars(input_string):
    # Define a regular expression to match invisible characters
    invisible_char_pattern = re.compile(r'[\uFE0F\u200B]+')
    
    # Remove all occurrences of invisible characters
    cleaned_string = invisible_char_pattern.sub('', input_string)
    
    return cleaned_string


# def entity_annotation(doc, tweet):
#     labels = ["players", "teams"]
#     for label in labels:
#         index = "all_" + label
#         spans = find_non_overlapping_occurences(tweet[index], doc.text) 
#         for span in spans:
#             start = doc.text[span[0]]
#             end = doc.text[span[1]-1]
#             spacy_span = doc.char_span(span[0], span[1], label=label[:-1].upper())
#             try:
#                 doc.ents = list(doc.ents) + [spacy_span]
#             except:
#                 print("Error with entity annotation", start, end, span, doc.text)
                
#     return doc

def entity_annotation_new(doc, tweet):
    relation_instances = get_relations_string(tweet)
    ent_strings = {}
    ent_strings["players"], ent_strings["teams"] = get_players_and_teams_from_instances(relation_instances)
    
    
    #'dictionary' has to be a list since lists cannot be used as the key of a dictionary in Python
    text_to_ent_dict = ([],[])
    
    #print(ent_strings)
    
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
        
                
    return instances_string

def get_relations_ent(instances_string, text_to_ent_dict):
    new_instances = []
    for instance in instances_string:
        new_instance = [text_to_ent_dict[1][text_to_ent_dict[0].index(instance[0])], text_to_ent_dict[1][text_to_ent_dict[0].index(instance[1])], instance[2]]
        new_instances.append(new_instance)

    return new_instances
    
def modify_doc_relations(doc, instances_ent):  
    for instance in instances_ent:
        for player_ent in instance[0]:
            for team_ent in instance[1]:
                offset = (player_ent.start, team_ent.start)
                if offset not in doc._.rel:
                    doc._.rel[offset] = {"plays_for": 0.0, "rumoured_to_join": 0.0}
                if instance[2] != "none":
                    doc._.rel[offset][instance[2]] = 1.0
        
    # instances = doc._.rel.keys()
    # for i, instance1 in enumerate(instances):
    #     for instance2 in enumerate(instances[i+1:]):
    #         if abs(instance1[1] - instance2[1]) <= 2:
    #             doc._.rel[instance1] = {"plays_for": 0.5, "rumoured_to_join": 0.5}
    #             doc._.rel[instance2] = {"plays_for": 0.5, "rumoured_to_join": 0.5}
                



        # offset = (instance[0][0].start, instance[1][0].start)
        # if offset not in doc._.rel:
        #     doc._.rel[offset] = {"plays_for": 0.0, "rumoured_to_join": 0.0}
        # doc._.rel[offset][instance[2]] = 1.0
    
    return doc

def modify_doc_for_entity_resolution(doc, player_ents_grouped, team_ents_grouped):
    all_player_ents = []
    for player_ent_group in player_ents_grouped:
        all_player_ents.extend(player_ent_group)
    all_team_ents = []
    for team_ent_group in team_ents_grouped:
        all_team_ents.extend(team_ent_group)
    for ents in [all_player_ents, all_team_ents]:
        for i, ent1 in enumerate(ents[:-1]):
            for ent2 in ents[i+1:]:
                offset = (ent1.start, ent2.start)
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
        if len(tweet["transfers"]) == 0:
            continue
        cleaned_text = remove_invisible_chars(tweet["text"])
        doc = nlp(cleaned_text)
        doc = entity_annotation_new(doc, tweet)
        #print(doc._.rel)
        db.add(doc)
    return db

# def entity_annotation_from_list(data):
#     db = DocBin()
#     for tweet in data:
#         cleaned_text = remove_invisible_chars(tweet["text"])
#         doc = nlp(cleaned_text)
#         labels = ["players", "teams"]
#         for label in labels:
#             index = "all_" + label
#             spans = find_non_overlapping_occurences(tweet[index], doc.text) 
#             for span in spans:
#                 start = doc.text[span[0]]
#                 end = doc.text[span[1]-1]
#                 spacy_span = doc.char_span(span[0], span[1], label=label[:-1].upper())
#                 try:
#                     doc.ents = list(doc.ents) + [spacy_span]
#                 except:
#                     print("Error with entity annotation", start, end, span, doc.text)
                
#             for token in doc:
#                 if token.ent_iob_ != "O":
#                     #print(token.text, token.ent_iob_ + "-" +  token.ent_type_)
#                     print(token.text, token.ent_type)
#                 else:
#                     print(token.text, token.ent_type)
#             print("--------------------------------")
#         db.add(doc)
#     return db

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
        "text": "❗️News #Mamardashvili: He definitely WON‘T join FC Bayern! It’s decided ✅\n\n➡️ There were talks, yes. But it was never advanced as always reported. \n\nℹ️ Still NO 🟢 light for Yann Sommer from Bayern! He’s not allowed to join \n@Inter\n at this stage. Bayern is in control as there’s no secret option to buy. \n\n@SkySportDE\n 🇬🇪",
        "is_rumour": True,
        "all_players": ["#Mamardashvili", "Yann Sommer"],
        "all_teams": ["FC Bayern", "Bayern", "@Inter"],
        "transfers": [
            {
                "involved_players": ["#Mamardashvili"],
                "current_teams": [],
                "rumoured_teams": ["FC Bayern", "Bayern"],
                "bid_fees": [],
                "stage": "deal_off"
            },
            {
                "involved_players": ["Yann Sommer"],
                "current_teams": ["FC Bayern", "Bayern"],
                "rumoured_teams": ["@Inter"],
                "bid_fees": [],
                "stage": "personal_terms_agreed"
            }
        ]
    }
]

data2 = open_json("../tweets2.json")
#data2 = augment_data(data2)
db = annotation_from_list(data2)
db.to_disk("./tweets2.spacy")   