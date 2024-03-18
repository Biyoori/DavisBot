import random

path = "quotes.txt"

def getQuote():
    try:
        with open(path, encoding="utf-8") as file:
            quotes = (file.readlines())
            return random.choice(quotes)
    except FileNotFoundError:
        print("Quote file not found")