from transfermarktscraper import scraper
from transfermarktscraper import normalise_data

data = ["#SouthamptonFC", "#s04", "#BVB", "#FCBayern", "#FCBayernMünchen", "#CFC", "@bayer04_fussball"]

for string in data:
    print(normalise_data.handle_twitter_name(string))
