import spacy
from spacy.tokens import DocBin
import relation_component
import relation_extraction
import entity_resolver
import entity_resolver_model

db = DocBin().from_disk("tweets2.spacy")

nlp = spacy.blank("en")

def get_instances(doc):
    max_length = 0
    instances = []
    for player in [e for e in doc.ents if e.label_ == "PLAYER"]:
        for team in [e for e in doc.ents if e.label_ == "TEAM"]:
            if not max_length or abs(team.start - player.start) <= max_length:
                instances.append((player, team))
                #print("added")
    return instances

for doc in db.get_docs(nlp.vocab):
    print(doc.text)
    print(get_instances(doc))
    for ent in doc.ents:
        print(ent.text, ent.label_, ent.start)
    print("----------------------")