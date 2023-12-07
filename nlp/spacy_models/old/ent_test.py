import spacy
import relation_component
import relation_extraction

nlp = spacy.load("ner_model_v2/model-best")

doc = nlp("Blaise Matuidi to Inter Miami is a done deal. Total agreement reached today with Juventus. Medicals scheduled. Here we go 🤝⚪️⚫️ @SkySport #transfers")

for ent in doc.ents:
    print(ent.text, ent.label_)
#print(doc._.rel)