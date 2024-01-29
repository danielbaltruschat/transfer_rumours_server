import pandas as pd
from langdetect import detect
from deep_translator import GoogleTranslator
import os
import json
import csv

#Get all csv files in the directory
path = os.getcwd()
files = os.listdir(path + '/scraped_tweets')
files_csv = [f for f in files if f.endswith('csv')]

content = []
for file in files_csv:
    with open('scraped_tweets/' + file, 'r', encoding="utf8") as f:
        reader = csv.reader(f)
        #Get the 'content' column from the csv file
        #first_line = True
        for row in reader:
            # if first_line == True:
            #     first_line = False
            if reader.line_num > 1:
                content.append(row[2])
    
for text in content:
    #Detect the language of the tweet
    lang = detect(text)
    #If the language is not English, translate it to English
    if lang != 'en':
        text = GoogleTranslator(source='auto', target='en').translate(text)
    #Write the tweet to a json file
    with open('tweets.json', 'a') as f:
        json.dump(text, f)
        f.write('\n')
        
