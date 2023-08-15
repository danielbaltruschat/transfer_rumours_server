from setfit import SetFitModel

model = SetFitModel.from_pretrained("nlp/categorisation_model")


# class TweetCategorisationModel:
#     def __init__(self):
#         from setfit import SetFitModel
#         self.model = SetFitModel.from_pretrained("nlp/categorisation_model")
        
#     def is_rumour(self, text):
#         pred_list = self.model.predict([text])
#         return pred_list[0] == "rumour"

def is_rumour(text):
    pred_list = model.predict([text])
    return pred_list[0] == "rumour"

# print("Model loaded")
# preds = model.predict(["I really need to get a new sofa.", '''Excl: Anderlecht are now trying to hijack Barcelona move to sign former Chelsea talent Tudor Mendel 🚨🟣 #transfers

# Barça verbally agreed personal terms with Mendel to sign him as free agent for U21 team but Anderlecht making last minute attempt.''', '''Atalanta coach Gasperini: “Højlund and Man Utd? Sometimes there are choices to make and also agents… we all have to consider the financial factor”. 🔴🇩🇰

# “He’s very happy here, I’d love to keep Rasmus of course but sometimes clubs and also players have to consider huge bids”.'''])

    
# for pred in preds:
#     print(pred)
    