import nlp

def main():
    
    print("loaded")
    text = """LeBron James is rumoured to go to Real Madrid."""


    pass
    

    pass

    test = nlp.interpret_source(text)
    
    print("doc._.resolved:", test._.resolved)
    print()
    print("doc._.rel:", test._.rel)
    
    print("\ndoc._.normalised_names:")
    for ent in test._.normalised_names:
        if ent == -1:
            print("-1")
            continue
        print("Item.name:", ent.name, ", Item.url:", ent.url)
        
    print("\ndoc._.transfers:", test._.transfers)
        
    print("\nents:")
    for ent in test.ents:
        print("ent_text:", ent.text, ", ent_start:", ent.start, ", ent_label:", ent.label_)
        
    print("\ndoc._.ent_groups:", test._.ent_groups)
    
    print("\ndoc._.ent_start_dict:", test._.ent_start_dict)
    

main()
