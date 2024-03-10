from nlp.normalise_data import *

item = normalise_names(["Smith"], "player", "AFC Bournemouth")
print("Item:", item, ", Item.name:", item.name, ", Item.url:", item.url, ", Item.item_type:", item.item_type)

