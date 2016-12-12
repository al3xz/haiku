"""
This module gets inspiring set texts and outputs nouns with related adjectives.

Gutenberg and Brown corpora are currently supported. The module also generates word2vec model for inspiring set.
"""

import os
import re
import nltk
from nltk.corpus import cmudict
from gensim.models import word2vec
from nltk.corpus import brown

# TODO: comment these out once you have them
nltk.download('averaged_perceptron_tagger')
nltk.download('cmudict')
nltk.download('brown')

d = cmudict.dict()

def nsyl(word):
    """Syllable count"""
    # TODO - may work wrong
    return [len(list(y for y in x if str.isdigit(y[-1]))) for x in d[word.lower()]][0]

def get_file(file_name = 'alice.txt', url='http://www.gutenberg.org/cache/epub/19033/pg19033.txt'):
    """Getting file from Gutenberg"""
    file_raw = None

    if not os.path.isfile(file_name):
        from urllib import request
        response = request.urlopen(url)
        file_raw = response.read().decode('utf8')
        with open(file_name, 'w', encoding='utf8') as f:
            f.write(file_raw)
    else:
        with open(file_name, 'r', encoding='utf8') as f:
            file_raw = f.read()

    # Remove the start and end bloat from Project Gutenberg (this is not exact, but
    # easy).
    pattern = r'\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .+ \*\*\*'
    end = "End of the Project Gutenberg"
    start_match = re.search(pattern, file_raw)
    if start_match:
        start_index = start_match.span()[1] + 1
    else:
        start_index = 0
    end_index = file_raw.rfind(end)
    file = file_raw[start_index:end_index]

    return file

nouns = {}


def parse_sentence(sentence):
    """Get nouns with adjectives from sentence"""
    global nouns

    pattern = "NP: {<DT>?<JJ>*<NN>}"
    # define a tag pattern of an NP chunk
    NPChunker = nltk.RegexpParser(pattern)
    # create a chunk parser
    result = NPChunker.parse(sentence)
    for np in result:
        if type(np) is nltk.Tree and np.label() == 'NP':
            # print(np)
            noun = None
            adjectives = []
            for pos in np:
                if pos[1] == 'NN':
                    noun = pos[0]
                if pos[1] == 'JJ':
                    adjectives.append(pos[0])

            if noun is not None and len(adjectives) > 0:
                if noun not in nouns:
                    nouns[noun] = adjectives
                else:
                    for adj in adjectives:
                        if not adj in nouns[noun]:
                            nouns[noun].append(adj)


def process_sentences(sentences, tokenize=True):
    """Loop sentences and process them"""
    for sentence in sentences:
        if tokenize:
            text = nltk.tokenize.word_tokenize(sentence)
        else:
            text = sentence
        sentence_pos_tagged = nltk.pos_tag(text)
        # a simple sentence with POS tags
        # sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"), ("dog", "NN"), ("barked", "VBD"), ("at", "IN"), ("the", "DT"), ("cat", "NN")]
        parse_sentence(sentence_pos_tagged)
        # pass


if __name__ == "__main__":

    file_name = 'nouns_brown.txt'

    # Get all files
    # alice = get_file()
    # looking_glass = get_file('looking_glass.txt','http://www.gutenberg.org/files/12/12-0.txt')
    # dickens = get_file('dickens.txt', "https://www.gutenberg.org/files/580/580-0.txt")
    dorian = get_file('dorian_gray.txt', "http://www.gutenberg.org/cache/epub/174/pg174.txt")

    # Process all files
    #sentences = nltk.tokenize.sent_tokenize(dorian)

    # get texts from brown corpus
    sentences = brown.sents(categories=['adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies',
        'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance',
        'science_fiction'])

    # print(sentences[0])
    process_sentences(sentences, tokenize=False)
    model = word2vec.Word2Vec(sentences)
    model.save(file_name + ".word2vec")
    # model_org = word2vec.Word2Vec.load_word2vec_format('vectors.bin', binary=True)
    # sentences = nltk.tokenize.sent_tokenize(alice)
    # process_sentences(sentences)
    # sentences = nltk.tokenize.sent_tokenize(looking_glass)
    # process_sentences(sentences)
    # # TODO: may be Dickens is not for haikus
    # sentences = nltk.tokenize.sent_tokenize(dickens)
    # process_sentences(sentences)

    # Write the file with nouns and adjectives out
    with open(file_name, 'w') as f:
        for noun in nouns.keys():
            try:
                if (len(nouns[noun]) > 2) and noun in model.vocab.keys():
                    # filter nouns with more than 2 adjectives
                    line = noun + " " + str(nsyl(noun))
                    for adj in nouns[noun]:
                        line += " " + adj + " " + str(nsyl(adj))
                    f.write(line + "\n")
            except:
                continue

