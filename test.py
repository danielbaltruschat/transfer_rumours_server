from nlp.transfermarktscraper import scraper
import nlp

import sys

def main():
    
    print("loaded")
    text = "🚨🔴🇳🇱 #PL |\n\n◉ Bayern Munich and Liverpool reached an agreement for Ryan Gravenberch ‼️\n\n◉ 50M€ bonuses included 🔥"


    pass
    

    pass

    test = nlp.interpret_source(text)
    print(test)
    print(test._.normalised_names)
    for ent in test.ents:
        print(ent.text, ent.start, ent.label_)
    print(test._.ent_groups)
    print(test._.transfers)

main()
