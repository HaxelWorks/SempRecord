import pickle
from random import choice    


def generate_filename():

    # load the corpus from the pickle file
    with open('corpus.pkl', 'rb') as f:
        corpus = pickle.load(f)
        verbs = corpus['verbs']
        nouns = corpus['nouns']
        adjs = corpus['adjectives']
        
    if choice([True, False]):
        return choice(adjs) + "_" + choice(nouns)
    else:
        return choice(verbs) + "ing_" + choice(nouns)
    
    
if __name__ == "__main__":
    # generate 20 filenames
    for i in range(20):
        print(generate_filename())
        print('\n')
