import spacy
#from spacy_models import relation_extraction, relation_component, entity_resolver_component, entity_resolver_model
from . import format_rel_resolver_predictions
from . import normalise_data
import json

def open_json(json_file):
    with open(json_file, encoding="utf-8") as file:
        data = json.load(file)
    return data

#nlp = spacy.load("rel_model_v2/model-best")
nlp = spacy.load("nlp/spacy_models/full_model_v1/model-best")
nlp.add_pipe("add_ent_start_dict")
nlp.add_pipe("group_entities")
#nlp.add_pipe("mark_uncertain_relations")
nlp.add_pipe("format_rel_resolver_predictions")
nlp.add_pipe("normalise_groups")

print("loaded")

# doc = nlp("Excl. News Agustín #Rogel: Bobic has been in 🇦🇷 in the last days to push negotiations with the 24 y/o central defender from Estudiantes. Intensive talks took place. He‘s a free agent in January 2023. Hertha is proofing a permanent deal in this window. \n@Sky_Marc\n \n@SkySportDE\n 🇺🇾")

# for tweet in open_json("tweets2.json"):
#     doc = nlp(tweet["text"])
#     print(doc._.normalised_names)        

    
doc = nlp("🚨 EXCLUSIVE: Bayern are closing in on deal to sign 17 year old talent Nestory Irankunda, here we go! 🌟\n\n2006 born winger on the verge of joining Bayern in 2024 from Australian side Adelaide United.\n\nUnderstand fee verbally agreed is £3m fixed fee plus add-ons.")
print(doc._.normalised_names)