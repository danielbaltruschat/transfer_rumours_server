import spacy
from spacy.tokens import Doc, DocBin
from spacy.language import Language
from .spacy_models import relation_extraction, relation_component, entity_resolver_component, entity_resolver_model
from . import transfermarktscraper, normalise_data

Doc.set_extension("ent_groups", default=[], force=True)
Doc.set_extension("ent_start_dict", default = {}, force=True)
Doc.set_extension("transfers", default={}, force=True)
Doc.set_extension("normalised_names", default=[], force=True)

# db = DocBin().from_disk("spacy_models/tweets2.spacy")
# nlp = spacy.blank("en")

# class EntGroup:
#     def __init__(ent_start_list, ent_start_dict):
#         self.ent_start_list = ent_start_list
#         ent1 = ent_start_dict[ent_start_list[0]].label_
#         self.label = ent1.label_
        


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

# @Language.component("mark_uncertain_relations")
# def mark_uncertain_relations(doc):
#     instances = doc._.rel.keys()
#     for i, instance1 in enumerate(instances):
#         for instance2 in enumerate(instances[i+1:]):
#             if abs(instance1[1] - instance2[1]) <= 2:
#                 doc._.rel[instance1] = {"plays_for": 0.5, "rumoured_to_join": 0.5}
#                 doc._.rel[instance2] = {"plays_for": 0.5, "rumoured_to_join": 0.5}

#     return doc



@Language.component("format_rel_resolver_predictions")
def format_rel_resolver_predictions(doc):
    THRESHOLD = 0.7
    
    #relation predictions are between all entities so a majority voting system will be employed to see if one ent_group has relation with the other ent group
    def determine_relation_between_two_groups(doc, group1, group2, threshold):
        votes = {"plays_for": 0, "rumoured_to_join": 0}
        for ent_start1 in group1:
            for ent_start2 in group2:
                # for instance in ((ent_start1, ent_start2), (ent_start2, ent_start1)):
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


@Language.component("normalise_groups")
def normalise_groups(doc):
    #get all indexes involved
    indexes_involved = [item for tuple_ in doc._.transfers.keys() for item in tuple_]
    player_indexes = []
    doc._.normalised_names = [-1 for _ in range(len(doc._.ent_groups))]
    for i, group in enumerate(doc._.ent_groups):
        if i in indexes_involved:
            ent = doc._.ent_start_dict[group[0]]
            if ent.label_ == "PLAYER":
                player_indexes.append(i)
            else:
                #this code runs if the ent's label is 'TEAM'
                name_group = [doc._.ent_start_dict[ent_start].text for ent_start in group] #get list of strings from list of ent_starts
                normalised = normalise_data.normalise_names(name_group, "team") #returns an instance of Item class defined in scraper.py
                doc._.normalised_names[i] = normalised
        # else:
        #     doc._.normalised_names.append(-1)
        
    def find_current_team_for_player(transfers, index):
        for key, relation in transfers.items():
            if relation == "plays_for":
                if key[0] == index:
                    return key[1]
                elif key[1] == index:
                    return key[0]
        return None

    def find_uncertain_teams_for_player(transfers, index):
        uncertain_team_keys = []
        for key, relation in transfers.items():
            if relation == "uncertain":
                if key[0] == index:
                    uncertain_team_keys.append(key[1])
                elif key[1] == index:
                    uncertain_team_keys.append(key[0])
        return uncertain_team_keys
            
    """
    TRY CURRENT_TEAM
    TRY RUMOURED_TEAM
    TRY PLAYER without
    """

    for player_index in player_indexes:
        current_team_index = find_current_team_for_player(doc._.transfers, player_index)
        uncertain_teams_indexes = find_uncertain_teams_for_player(doc._.transfers, player_index)
        
        group = doc._.ent_groups[player_index]
        name_group = [doc._.ent_start_dict[ent_start].text for ent_start in group] 
        
        if current_team_index == None or doc._.normalised_names[current_team_index] == -1:
            normalised = normalise_data.normalise_names(name_group, "player")
            if len(uncertain_teams_indexes) >= 2:
                for i, item in enumerate(doc._.normalised_names):
                    if item != -1 and item.url == normalised.team_url:
                        doc._.transfers[(player_index, i)] = "plays_for"
                
                for team_index in uncertain_teams_indexes:
                    if doc._.transfers[(player_index, team_index)] != "plays_for":
                        doc._.transfers[(player_index, team_index)] = "rumoured_to_join"
                      
        else:
            current_team_name = doc._.normalised_names[current_team_index].name
            normalised = normalise_data.normalise_names(name_group, "player", current_team_name=current_team_name)

            if len(uncertain_teams_indexes) != 0:
                for uncertain_team_index in uncertain_teams_indexes:
                    doc._.transfers[(player_index, uncertain_team_index)] = "rumoured_to_join"
            
        doc._.normalised_names[player_index] = normalised
        
    return doc
        




