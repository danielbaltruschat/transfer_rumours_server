from torch import nn
import torch
import spacy
from spacy.tokens import DocBin
import relation_component
import relation_extraction

nlp = spacy.load("ner_model_v2/model-best")
db = DocBin().from_disk("data/train.spacy")

train_data = list(db.get_docs(nlp.vocab))



model  = nn.Sequential(
    nn.Linear(512, 5),
    nn.ReLU(),
    nn.Linear(5, 1),
    nn.Sigmoid()
)