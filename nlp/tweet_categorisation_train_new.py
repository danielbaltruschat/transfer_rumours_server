from sentence_transformers import SentenceTransformer
import torch
import torch.nn as nn

model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

sentences = ["🔴 Klopp on Super League: “I agree 100% with the statement and the verdict”.\n\n“I also like that we get an understanding that UEFA and other FAs can't just do what they want… putting in more games with people having no say in it”.\n\n“I like that UEFA & more got a bit of a shake”."]
embeddings = model.encode(sentences)
print(embeddings.shape)

class TextClassifier(nn.Module):
    def __init__(self, sentence_transformer_model):
        super(TextClassifier, self).__init__()
        self.sentence_transformer_model = sentence_transformer_model
        self.classification_layer = nn.Linear(in_features=sentence_transformer_model.config_hidden_size, out_features=1)
        

# json_file = open('tweets2.json', encoding="utf8")
# tweets_data = json.load(json_file)
