# import re

# text = "Ola Aina, set to sign two year deal at Nottingham Forest. 🔴🌳✍🏻 #NFFC\n\n It will also include an option for further season — potential contract until June 2026."
# print(text) # with emoji

# emoji_pattern = re.compile("["
#         u"\U0001F600-\U0001F64F"  # emoticons
#         u"\U0001F300-\U0001F5FF"  # symbols & pictographs
#         u"\U0001F680-\U0001F6FF"  # transport & map symbols
#         u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
#                            "]+", flags=re.UNICODE)
# print(emoji_pattern.sub(r'', text)) # no emoji

from cleantext import clean

text = "❗️More on #Sabitzer as exclusively revealed tonight! #BVB\n\n➡️ Understand there’s a TOTAL AGREEMENT between the clubs now! \n\n➡️ Transfer fee of around €19m with bonus payments included. \n\nSabitzer, on verge to join #BVB! Incredible turnaround ✅\n\n@SkySportDE\n 🇦🇹"

print(clean(text, fix_unicode=True))