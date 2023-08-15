import spacy
import json

json_file = open('tweets2.json', encoding="utf8")
tweets_data = json.load(json_file)

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

print(outliers)

# Load the spaCy language model:
nlp = spacy.load("en_core_web_sm")

# Add the "text_categorizer" pipeline component to the spaCy model, and configure it with SetFit parameters:
nlp.add_pipe("text_categorizer", config={
    "pretrained_model_name_or_path": "paraphrase-MiniLM-L3-v2",
    "setfit_trainer_args": {
        "train_dataset": train_dataset
    }
})


doc = nlp("I really need to get a new sofa.")
print(doc.cats)
doc2 = nlp('''Excl: Anderlecht are now trying to hijack Barcelona move to sign former Chelsea talent Tudor Mendel 🚨🟣 #transfers

Barça verbally agreed personal terms with Mendel to sign him as free agent for U21 team but Anderlecht making last minute attempt.''')
print(doc2.cats)

doc3 = nlp('''Atalanta coach Gasperini: “Højlund and Man Utd? Sometimes there are choices to make and also agents… we all have to consider the financial factor”. 🔴🇩🇰

“He’s very happy here, I’d love to keep Rasmus of course but sometimes clubs and also players have to consider huge bids”.''')
print(doc3.cats)


nlp.to_disk("model_artifacts")