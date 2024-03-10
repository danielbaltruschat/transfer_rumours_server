from setfit import SetFitModel

model = SetFitModel.from_pretrained("nlp/categorisation_model")

def is_rumour(text):
    pred_list = model.predict([text])
    return pred_list[0] == "transfer_rumour"

    