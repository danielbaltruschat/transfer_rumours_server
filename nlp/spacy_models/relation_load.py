import spacy
import relation_component
import relation_extraction
import entity_resolver_component
import entity_resolver_model

#nlp = spacy.load("rel_model_v2/model-best")
nlp = spacy.load("full_model_v1/model-best")
print("loaded")

doc = nlp("Excl. News Agustín #Rogel: Bobic has been in 🇦🇷 in the last days to push negotiations with the 24 y/o central defender from Estudiantes. Intensive talks took place. He‘s a free agent in January 2023. Hertha is proofing a permanent deal in this window. \n@Sky_Marc\n \n@SkySportDE\n 🇺🇾")

def get_relation_from_scores(threshold, relation_scores):
    for label, score in relation_scores.items():
        if score > threshold:
            return label

def get_relations_ent(doc):
    ent_start_dict = {}
    for ent in doc.ents:
        ent_start_dict[ent.start] = ent
    
    relations = {}
    for ent_starts, relation_scores in doc._.rel.items():
        label = get_relation_from_scores(0.5, relation_scores)
        player = ent_start_dict[ent_starts[0]]
        team = ent_start_dict[ent_starts[1]]
        relations[(player, team)] = label
            
    return relations
        

    

for ent in doc.ents:
    print(ent.text, ent.label_, ent.start)

print(doc._.rel)
print(doc._.resolved)
print(get_relations_ent(doc))