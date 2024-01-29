from nlp.transfermarktscraper import scraper
import nlp

import sys

def main():
    
    print("loaded")
    text = """🚨🆕 News #Mangala: There was direct contact between Juventus and the player in the last days 📞\n\n➡️ @juventusfc is still interested in a six-months-loan with an option to buy. But: Allegri will make the final decision ✔️\n\nNapoli have submitted an offer in the last days as revealed. Forest has rejected the initial first offer from Galatasaray. @SkySportDE 🇧🇪"""


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
