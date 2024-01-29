import spacy
from spacy.language import Language
from spacy.tokens import Doc


if not Doc.has_extension("resolved"):
        Doc.set_extension("resolved", default={})
        
        
@Language.component("entity_resolver")
def entity_resolver(doc):
    temp_dict = {}
    for ent in doc.ents:
        if ent.label_ in temp_dict.keys():
            temp_dict[ent.label_].append(ent)
        else:
            temp_dict[ent.label_] = [ent]
        
    for label, ents in temp_dict.items():
        resolved = []
        ents = sorted(ents, key=lambda x: len(x), reverse=True)
        matched = [False for _ in range(len(ents))]
        for i, ent1 in enumerate(ents):
            if matched[i]:
                continue
            else:
                group = [ent1]
                #resolved.append(ent1)
            for j, ent2 in enumerate(ents[i+1:]):
                if ent2.text in ent1.text:
                    #resolved.append(ent1)
                    group.append(ent2)
                    matched[j] = True
            resolved.append(group)
                      
        doc._.resolved[label] = resolved
        
        
    return doc