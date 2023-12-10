from nlp.transfermarktscraper import scraper
import nlp

import sys

def main():
    
    print("loaded")
    text = "🚨 EXCLUSIVE News Ronald #Araujo: He‘s the absolute desired transfer target of FC Bayern!\n\n‼️ There was a phone call between Tuchel, Freund and Araujo this Friday 📞\n\n➡️ Tuchel made it clear to him that he wants him urgently, preferably in winter or summer, no matter the cost. Bayern, ready to pay a massive transfer fee! \n\nIt will be a difficult mission for Bayern. Now it's up to Araújo. \n@SkySportDE\n 🇺🇾\n"


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
