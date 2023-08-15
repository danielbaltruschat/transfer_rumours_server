# from transformers import AutoTokenizer, AutoModelForTokenClassification

# AutoTokenizer.from_pretrained("microsoft/SportsBERT")
# AutoModelForTokenClassification.from_pretrained("microsoft/SportsBERT")

from transformers import pipeline

question_answerer = pipeline("question-answering", model="deepset/roberta-base-squad2", tokenizer="deepset/roberta-base-squad2")

rumour = "❗️Alexander Nübel, a loan deal with \n@VfB\n is more and more possible as reported tonight. \n\nSecond offer wasn’t rejected yet. Bayern bosses are willing to find an agreement with Stuttgart. But payment terms are not 100 % agreed yet. \n\n➡️ It’s a loan offer WITHOUT an option to buy now \n➡️ Loan fee of around €1m. \n\nFinal decision expected this weekend.\n\n@_dennisbayer\n | \n@SkySportDE\n 🇩🇪"

player = question_answerer(question="What is the main player involved in this transfer rumour?", context=rumour)['answer']

rumoured_team = question_answerer(question="What team is {0} rumoured to transfer to?".format(player), context=rumour)['answer']

current_team = question_answerer(question="What team is {0} currently playing for?".format(player), context=rumour)['answer']

print("Player: {0}\nRumoured team: {1}\nCurrent team: {2}".format(player, rumoured_team, current_team))