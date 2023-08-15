import json
import torch
from transformers import BertTokenizer, BertForTokenClassification
from torch.utils.data import DataLoader, Dataset
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW
from tqdm import tqdm

# Define the labels for NER (player, current_team, rumored_team, etc.)
labels = ["O", "B-player", "I-player", "B-current_team", "I-current_team", "B-rumored_team", "I-rumored_team"]

# Define a mapping of labels to label IDs for the model
label_map = {label: i for i, label in enumerate(labels)}

# Load the pre-trained BERT model and tokenizer
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForTokenClassification.from_pretrained(model_name, num_labels=len(labels))

# Load and process the data from the JSON file
def load_data_from_json(json_file):
    with open(json_file, encoding="utf-8") as file:
        data = json.load(file)
    return data 

# Convert the data to a format suitable for training
class TransferRumorDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item["text"]
        labels = self._convert_labels_to_ids(text, item["transfers"])
        return text, labels

    def _convert_labels_to_ids(self, text, transfers):
        # Initialize label_ids list with "O" (Outside) for each token in the text
        label_ids = [label_map["O"]] * len(tokenizer.tokenize(text))

        for transfer in transfers:
            for player in transfer["involved_players"]:
                player_tokens = tokenizer.tokenize(player)
                label_ids[player_tokens.index(player_tokens[0])] = label_map["B-player"]
                for i in range(1, len(player_tokens)):
                    label_ids[player_tokens.index(player_tokens[i])] = label_map["I-player"]

            for team in transfer["current_teams"]:
                team_tokens = tokenizer.tokenize(team)
                label_ids[team_tokens.index(team_tokens[0])] = label_map["B-current_team"]
                for i in range(1, len(team_tokens)):
                    label_ids[team_tokens.index(team_tokens[i])] = label_map["I-current_team"]

            for team in transfer["rumoured_teams"]:
                team_tokens = tokenizer.tokenize(team)
                label_ids[team_tokens.index(team_tokens[0])] = label_map["B-rumored_team"]
                for i in range(1, len(team_tokens)):
                    label_ids[team_tokens.index(team_tokens[i])] = label_map["I-rumored_team"]

        return label_ids

# Training function
def train_model(model, train_dataloader, epochs=3, learning_rate=5e-5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    optimizer = AdamW(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for batch in tqdm(train_dataloader, desc=f"Epoch {epoch + 1}", unit="batch"):
            texts, labels = batch
            inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            labels = torch.tensor(labels).to(device)

            outputs = model(**inputs, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch + 1} - Average Loss: {total_loss / len(train_dataloader)}")

# Load the data
data = load_data_from_json("tweets2.json")

# Create the dataset and dataloader
dataset = TransferRumorDataset(data, tokenizer)
train_dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Train the NER model
train_model(model, train_dataloader)
