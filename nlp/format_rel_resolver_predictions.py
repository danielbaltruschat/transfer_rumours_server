import spacy
from spacy.tokens import Doc, DocBin
from spacy.language import Language
from .spacy_models import relation_extraction, relation_component, entity_resolver_component, entity_resolver_model

Doc.set_extension("ent_groups", default=[], force=True)
Doc.set_extension("ent_start_dict", default = {}, force=True)
Doc.set_extension("transfers", default={}, force=True)
Doc.set_extension("normalised_names", default=[], force=True)

@Language.component("add_ent_start_dict")
def add_ent_start_dict(doc):
    for ent in doc.ents:
        doc._.ent_start_dict[ent.start] = ent
    return doc

@Language.component("group_entities")
def group_entities(doc, threshold=0.5):
    #predictions are in the format (ent1.start, ent2.start): score

    #adds entities which are in resolved
    for ent_starts, prediction in doc._.resolved.items():
        if prediction > threshold:
            group_exists = False
            for group in doc._.ent_groups:
                if ent_starts[0] in group or ent_starts[1] in group:
                    group_exists = True
                    if ent_starts[0] not in group:
                        group.append(ent_starts[0])
                    if ent_starts[1] not in group:
                        group.append(ent_starts[1])
            if not group_exists:
                doc._.ent_groups.append([ent_starts[0], ent_starts[1]])

    #when there is only one player or team entity they are not in doc._.resolved so this adds them
    for ent in doc.ents:
        in_ent_groups = False
        for group in doc._.ent_groups:
            if ent.start in group:
                in_ent_groups = True
                break
        if not in_ent_groups:
            doc._.ent_groups.append([ent.start])

    return doc



@Language.component("format_rel_resolver_predictions")
def format_rel_resolver_predictions(doc):
    THRESHOLD = 0.7
    
    #relation predictions are between all entities so a majority voting system will be employed to see if one ent_group has relation with the other ent group
    def determine_relation_between_two_groups(doc, group1, group2, threshold):
        votes = {"plays_for": 0, "rumoured_to_join": 0}
        for ent_start1 in group1:
            for ent_start2 in group2:
                if (ent_start1, ent_start2) in doc._.rel.keys():
                    prediction = doc._.rel[(ent_start1, ent_start2)]
                elif (ent_start2, ent_start1) in doc._.rel.keys():
                    prediction = doc._.rel[(ent_start2, ent_start1)]
                else:
                    continue
                
                for label in votes.keys():
                    if prediction[label] > threshold:
                        votes[label] += 1
                        
        if votes["plays_for"] > votes["rumoured_to_join"]:
            return "plays_for"
        elif votes["rumoured_to_join"] > votes["plays_for"]:
            return "rumoured_to_join"
        else:
            return "uncertain"
                        
    player_groups = []
    team_groups = []
    for group in doc._.ent_groups:
        ent = doc._.ent_start_dict[group[0]]
        if ent.label_ == "PLAYER":
            player_groups.append(group)
        elif ent.label_ == "TEAM":
            team_groups.append(group)
        else:
            raise Exception("Entity label is not PLAYER or TEAM.")
        
    for player in player_groups:
        for team in team_groups:
            relation = determine_relation_between_two_groups(doc, player, team, THRESHOLD)

            #use indexing rather than just appending the group to the list as the index will be used to reference the group with normalised data
            player_index = doc._.ent_groups.index(player)
            team_index = doc._.ent_groups.index(team)
            doc._.transfers[(player_index, team_index)] = relation


    return doc



        




