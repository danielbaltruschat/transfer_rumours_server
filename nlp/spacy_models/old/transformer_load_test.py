import spacy

nlp = spacy.load("ner_model_transformer/model-best")

doc = nlp("Martin Dubravka is gonna sign the contract as new Manchester Utd player in the next few hours. It’s done, sealed with both player and Newcastle side. 100%. 🔴🤝 #MUFC\n\nHere we go confirmed.")

for ent in doc.ents:
    print(ent.text, ent.label_)
    
pass