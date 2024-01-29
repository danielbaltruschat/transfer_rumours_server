import json
import spacy
from spacy.tokens import DocBin
import re
from langdetect import detect
import dl_translate as dlt

'''
Example entry:
{
    "text": "Negotiations advancing for Anthony Elanga to Nottingham Forest — it’d be permanent deal. 🔴🌳👀 #NFFC",
    "is_rumour": true,
    "all_players": ["Anthony Elanga"],
    "all_teams": ["Nottingham Forest"],
    "transfers": [
        {
            "involved_players": ["Anthony Elanga"],
            "current_teams": [],
            "rumoured_teams": ["Nottingham Forest"],
            "bid_fees": [],
            "stage": "negotations"
        }
    ]
}
'''

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

def entity_annotation_from_list(data):
    db = DocBin()
    for tweet in data:
        cleaned_text = remove_invisible_chars(tweet["text"])
        doc = nlp(cleaned_text)
        entities = tweet["transfers"][:1]
        if len(entities) != 0:
            indexes = ["involved_players", "current_teams", "rumoured_teams"]
            for index in indexes:
                spans = get_char_spans(doc.text, entities, index)
                for span in spans:
                    spacy_span = doc.char_span(span[0], span[1], label=index[:-1].upper())
                    doc.ents = list(doc.ents) + [spacy_span]
                
            for token in doc:
                if token.ent_iob_ != "O":
                    #print(token.text, token.ent_iob_ + "-" +  token.ent_type_)
                    print(token.text, token.ent_type)
                else:
                    print(token.text, token.ent_type)
            print("--------------------------------")
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

def entity_annotation_from_list_all(data):
    db = DocBin()
    for tweet in data:
        cleaned_text = remove_invisible_chars(tweet["text"])
        doc = nlp(cleaned_text)
        entities = tweet["transfers"][:1]
        if len(entities) != 0:
            indexes = ["involved_players", "current_teams", "rumoured_teams"]
            for index in indexes:
                spans = get_char_spans(doc.text, entities, index)
                for span in spans:
                    spacy_span = doc.char_span(span[0], span[1], label=index[:-1].upper())
                    doc.ents = list(doc.ents) + [spacy_span]
                
            for token in doc:
                if token.ent_iob_ != "O":
                    #print(token.text, token.ent_iob_ + "-" +  token.ent_type_)
                    print(token.text, token.ent_type)
                else:
                    print(token.text, token.ent_type)
            print("--------------------------------")
        db.add(doc)
    return db

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

data2 = open_json("tweets2.json")
#data2 = augment_data(data2)
db = entity_annotation_from_list(data2)
db.to_disk("./tweets.spacy")   
        
    