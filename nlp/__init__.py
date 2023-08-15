from deep_translator import GoogleTranslator
from .spacy_load_ner import NER
from . import tweet_categorisation_load
from langdetect import detect

# def interpret_source(text, categorisation_model, ner_model):
#     try:
#         current_language = detect(text)
#     except Exception as e:
#         print("Language detection failed for '" + text + "'")
#         current_language = "en"
        
#     if current_language != "en":
#         translator = GoogleTranslator(source=current_language, target="en")
#         text = translator.translate(text)
    
#     is_rumour = categorisation_model.is_rumour(text)
#     if not is_rumour:
#         return [is_rumour, [], [], [], "unknown", -1]
    
#     ner = NER(text, ner_model)
    
    
#     return [is_rumour, ner.get_involved_players(), ner.get_current_teams(), ner.get_rumoured_teams(), "unknown", -1]


def interpret_source(text):
    try:
        current_language = detect(text)
    except Exception as e:
        print("Language detection failed for '" + text + "'")
        current_language = "en"
        
    if current_language != "en":
        translator = GoogleTranslator(source=current_language, target="en")
        text = translator.translate(text)
    
    is_rumour = tweet_categorisation_load.is_rumour(text)
    if not is_rumour:
        return [is_rumour, [], [], [], "unknown", -1]
    
    ner = NER(text)
    
    return [is_rumour, ner.get_involved_players(), ner.get_current_teams(), ner.get_rumoured_teams(), "unknown", -1]
    
#print(interpret_source("Excl: Anderlecht are set to sign Ludwig Augustinsson as new fullback on loan from Sevilla until June 2024 🚨🟣🇸🇪\n\nFormer Aston Villa player will travel soon for medical tests."))


