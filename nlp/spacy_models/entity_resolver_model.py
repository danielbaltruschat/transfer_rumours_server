from typing import List, Tuple, Callable

import spacy
from spacy.tokens import Doc, Span
from thinc.types import Floats2d, Ints1d, Ragged, cast
from thinc.api import Model, Linear, chain, Logistic

@spacy.registry.misc("resolver_instance_generator.v1")
def create_instances_resolver(max_length: int) -> Callable[[Doc], List[Tuple[Span, Span]]]:
    def get_instances(doc: Doc) -> List[Tuple[Span, Span]]:
        players = [e for e in doc.ents if e.label_ == "PLAYER"]
        teams = [e for e in doc.ents if e.label_ == "TEAM"]
        instances = []
        for ents in (players, teams):
            for i, ent1 in enumerate(ents[:-1]):
                for ent2 in ents[i+1:]:
                    instances.append((ent1, ent2))
        return instances
    return get_instances