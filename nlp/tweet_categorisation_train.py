from sentence_transformers.losses import CosineSimilarityLoss
from setfit import SetFitTrainer, SetFitModel
import json
import pandas as pd
from datasets import Dataset

json_file = open('tweets.json', encoding="utf8")
tweets_data = json.load(json_file)
tweets_table = pd.DataFrame(tweets_data)


#first three columns of tweets_table
tweets_table = tweets_table.iloc[:, :2]
print(tweets_table.head())

#replaces boolean with label in second column
tweets_table['is_rumour'] = tweets_table['is_rumour'].replace({True: 'transfer_rumour', False: 'not_transfer_rumour'})


inliers = []
outliers = []

for tweet in tweets_data:
    if tweet['is_rumour'] == True:
        inliers.append(tweet['text'])
    else:
        outliers.append(tweet['text'])
        
        
train_dataset = {
    "inlier": inliers,
    "outlier": outliers
}


def split_dataset(dataset, split_ratio=0.4):
    split_index = int(len(dataset) * split_ratio)
    return Dataset.from_pandas(dataset[:split_index]), Dataset.from_pandas(dataset[split_index:])

train_dataset, test_dataset = split_dataset(tweets_table)

trainer = SetFitTrainer(
    model = SetFitModel.from_pretrained("paraphrase-MiniLM-L3-v2"),
    train_dataset=train_dataset,
    loss_class=CosineSimilarityLoss,
    batch_size=16,
    num_iterations=20,
    column_mapping={"text": "text", "is_rumour": "label"}
)

trainer.train()
metrics = trainer.evaluate(test_dataset)
trainer.model.save_pretrained("categorisation_model")


model = SetFitModel.from_pretrained("categorisation_model")
preds = model.predict(["I really need to get a new sofa.", '''Excl: Anderlecht are now trying to hijack Barcelona move to sign former Chelsea talent Tudor Mendel 🚨🟣 #transfers

Barça verbally agreed personal terms with Mendel to sign him as free agent for U21 team but Anderlecht making last minute attempt.''', '''Atalanta coach Gasperini: “Højlund and Man Utd? Sometimes there are choices to make and also agents… we all have to consider the financial factor”. 🔴🇩🇰

“He’s very happy here, I’d love to keep Rasmus of course but sometimes clubs and also players have to consider huge bids”.'''])

    
for pred in preds:
    print(pred)
    
pass