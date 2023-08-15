import spacy
from spacy.training.example import Example
import json

# Load the spaCy English language model
nlp = spacy.load("en_core_web_sm")

# Sample data with labeled football teams and players
json_file = open('tweets2.json', encoding="utf8")
data = json.load(json_file)

training_data = []
for tweet in data:
    text = tweet['text']
    players = tweet['all_players']
    teams = tweet['all_teams']
    entities = []
    
    for player in players:
        start_idx = text.find(player)
        end_idx = start_idx + len(player)
        if start_idx != -1:
            entities.append((start_idx, end_idx, "player"))

    # Extract team entities and their spans
    for team in teams:
        start_idx = text.find(team)
        end_idx = start_idx + len(team)
        if start_idx != -1:
            entities.append((start_idx, end_idx, "team"))
    
    training_data.append((text, {"entities": entities}))
        

# Prepare the data for training
texts = [data[0] for data in training_data]
annotations = [data[1] for data in training_data]

# Create a blank "en" model with the ner component
nlp_ner = spacy.blank("en")
ner = nlp_ner.create_pipe("ner")
nlp_ner.add_pipe("ner")

# Add the labeled entity annotations to the NER model
for _, annotations in training_data:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipeline components during training
other_pipes = [pipe for pipe in nlp_ner.pipe_names if pipe != "ner"]

# Training the NER model
with nlp_ner.disable_pipes(*other_pipes):
    optimizer = nlp_ner.begin_training()
    for _ in range(20):  # You can adjust the number of iterations here
        losses = {}
        for text, annotations in zip(texts, annotations):
            nlp_ner.update([text], [annotations], drop=0.5, sgd=optimizer, losses=losses)
        print(losses)

# Test the trained NER model with some examples
test_data = [
    "Neymar is a skillful player.",
    "Arsenal is one of the top teams in England."
]

for text in test_data:
    doc = nlp_ner(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"Text: {text}\nEntities: {entities}\n")
