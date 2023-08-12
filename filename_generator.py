from collections import Counter
from random import choice
import os

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

if __name__ == "__main__":
    from collections import defaultdict
    from tqdm import tqdm
    import requests
    import pickle
    
    ENGLISH_CORPUS_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt"
    CORPUS = "english_corpus.txt"
    # Download a list of all words in the english language
    def download_corpus(url:str):
        
        r = requests.get(url)
        with open(CORPUS, "wb") as f:
            f.write(r.content)

    # check if the file exists
    if not os.path.exists(CORPUS):
        download_corpus(ENGLISH_CORPUS_URL)

    def filter_words(word: str):
        """ filter out words that non alphnaumeric or have a length less than 3 """
        if not word.isalpha():
            return False
        if len(word) < 3:
            return False
        return True
        
        
    with open(CORPUS, "r") as f:
        # read the file line by line
        words = [line.strip().lower() for line in f.readlines()]
        filtered_words = list(filter(filter_words, words))

    statdict = defaultdict(lambda: Counter())
    
    for word in tqdm(filtered_words):
        #iterate over all 3 len subsequences of the word
        l = len(word)
        fragments = [word[i:i+3] for i in range(l-2) ]
        for fragment in fragments:
            ab = fragment[0:2]
            c = fragment[2]
            statdict[ab][c] += 1
            
    # pickle the statdict
    with open('statdict.pkl', 'wb') as f:
        pickle.dump(dict(statdict), f)

else:
    # load the statdict
    import pickle
    with open('statdict.pkl', 'rb') as f:
        statdict = pickle.load(f)      
    

def generate_word(length=5, start=''):
    """ generate a new word using weighted random choices from statdict"""

    while not statdict[start]:
        # if the start is not in the statdict, get a new start
        start = choice(ALPHABET) + choice(ALPHABET)    
    
    try:
        word = start
        loops = length - len(start)
        for i in range(loops):
            ab = word[-2:]
            #get the next letter from the weighted random choices
            c = choice(list(statdict[ab].elements()))
            word += c
    except IndexError:
        #if at first you don't succeed, try again
        return generate_word(length, start)
    
    return word


# generate 100 words

# mumble = [generate_word()+"-"+generate_word() for i in range(100)]
# [print(word) for word in mumble]
