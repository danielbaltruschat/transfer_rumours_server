from deep_translator import GoogleTranslator
import spacy
from . import format_rel_resolver_predictions
from . import normalise_data
from . import tweet_categorisation_load
from langdetect import detect
    
nlp = spacy.load("nlp/spacy_models/full_model_v1/model-best")
nlp.add_pipe("add_ent_start_dict")
nlp.add_pipe("group_entities")
nlp.add_pipe("format_rel_resolver_predictions")
nlp.add_pipe("normalise_groups")

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
        return None
    
    doc = nlp(text)
    
    return {"normalised_names": doc._.normalised_names, "relations": doc._.transfers}
    
#print(interpret_source("Excl: Anderlecht are set to sign Ludwig Augustinsson as new fullback on loan from Sevilla until June 2024 🚨🟣🇸🇪\n\nFormer Aston Villa player will travel soon for medical tests."))


