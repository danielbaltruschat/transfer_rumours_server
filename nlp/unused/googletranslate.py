import dl_translate as dlt
from langdetect import detect

text = "Negotiations advancing for Anthony Elanga to Nottingham Forest — it’d be permanent deal. 🔴🌳👀 #NFFC"

mt = dlt.TranslationModel()

mt.save_obj("translation_model")

print(mt.available_languages())