import spacy

nlp = spacy.load("nlp/ner_model/model-best")

# class NERModel:
#     def __init__(self):
#         self.nlp = spacy.load("nlp/ner_model/model-best")

class NER:
    def __init__(self, text):
        self.__doc = nlp(text)
        ents = self.get_ents_list()
        self.__involved_players = []
        self.__current_teams = []
        self.__rumoured_teams = []
        for ent in ents:
            if ent.label_ == "INVOLVED_PLAYER":
                self.__involved_players.append(ent.text)
            elif ent.label_ == "CURRENT_TEAM":
                self.__current_teams.append(ent.text)
            elif ent.label_ == "RUMOURED_TEAM":
                self.__rumoured_teams.append(ent.text)
    
    def get_doc(self):
        return self.__doc
    
    def get_ents_list(self):
        return list(self.__doc.ents)
    
    def get_involved_players(self):
        return self.__involved_players
    
    def get_current_teams(self):
        return self.__current_teams
    
    def get_rumoured_teams(self):
        return self.__rumoured_teams

# doc = nlp("James Word-Prowse, in London tonight ahead of medical tests already booked on Friday. ⚒️🏴󠁧󠁢󠁥󠁮󠁧󠁿 #WHUFC\n\nHe’s joining West Ham — as agreement was reached on Wednesday, confirmed.\n\n🔴 Talks over personal terms with Harry Maguire continue.")

# for token in doc:
#     if token.ent_iob_ != "O":
#         print(token.text, token.ent_iob_ + "-" +  token.ent_type_)
#     else:
#         print(token.text, token.ent_iob_)