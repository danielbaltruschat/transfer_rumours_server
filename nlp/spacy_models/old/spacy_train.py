import spacy
from spacy.tokens import DocBin
import relation_component
import relation_extraction

docs = DocBin().from_disk("tweets2.spacy")

nlp = spacy.blank("en")
nlp.add_pipe("relation_extractor")