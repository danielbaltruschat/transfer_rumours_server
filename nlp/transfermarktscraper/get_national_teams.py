from bs4 import BeautifulSoup
import requests
import json

URL = "https://www.transfermarkt.co.uk/wettbewerbe/fifa?ajax=yw1&page="
HEADERS = {"User-Agent": "Mozilla/5.0"}

national_teams = []
    
for i in range(1, 10):
    page = requests.get(URL + str(i), headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    main = soup.find("main")

    rows = soup.find("tbody")

    odds = rows.find_all("tr", class_="odd")
    evens = rows.find_all("tr", class_="even")

    all_rows = odds + evens
        
    def get_name(row):
        field = row.find("td", class_="hauptlink")
        return field.find_all("a")[1].get_text().lower()

    for row in all_rows:
        national_teams.append(get_name(row))
        
with open("national_teams.json", "w") as f:
    json.dump(national_teams, f, indent=4)