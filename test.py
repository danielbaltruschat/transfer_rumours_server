from nlp.transfermarktscraper import scraper
import nlp

import sys

def main():
    
    print("loaded")
    text = """Real Madrid are pursuing Jude Bellingham! The club is pushing for a deal to be done before the end of the transfer window."""


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
