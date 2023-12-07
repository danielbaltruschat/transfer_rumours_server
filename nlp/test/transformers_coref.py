import spacy

nlp = spacy.load("ner_model_v2/model-best")

doc = nlp("Understand Bournemouth are currently not in talks to sign Ivan Fresneda despite recent links. Several clubs want Fresneda but #AFCB not working on it. 🍒🇪🇸")

for ent in doc.ents:
    print(ent.text, ent.label_)