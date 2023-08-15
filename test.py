from transfermarktscraper import scraper
from transfermarktscraper import normalise_data

from nlp import interpret_source

from deep_translator import GoogleTranslator


import sys

def main():
    
    
    text = "🚨🔴🔵🇵🇹 #Ligue1 |\n\n◉ Total agreement close to being found between Roma and PSG for the loan with OA of Renato Sanches.\n\n◉ OA will become mandatory if the player plays 30 matches. OA of €12m + bonus."


    pass
    

    pass

    test = interpret_source(text)
    print(test)
    test = normalise_data.normalise_data(test[1], test[2], test[3])
    print(test)

main()

pass

modules = list(sys.modules.keys())
modules2 = sys.modules

pass

del interpret_source

pass