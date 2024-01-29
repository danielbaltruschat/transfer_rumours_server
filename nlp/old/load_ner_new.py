import spacy

nlp = spacy.load("ner_model_v2/model-best")
nlp.add_pipe("relation_extractor")


doc = nlp("Excl: Manchester United are set to sign Martin Dúbravka, here we go! Full agreement reached, loan deal with buy option £5m not mandatory. It’s agreed with Newcastle and player side 🚨🔴 #MUFC\n\nDúbravka will travel tonight, medical on Tuesday.\n\nAntony and new 2d goalkeeper coming.")



for token in doc:
    if token.ent_iob_ != "O":
        print(token.text, token.ent_iob_ + "-" +  token.ent_type_)
    else:
        print(token.text, token.ent_iob_)