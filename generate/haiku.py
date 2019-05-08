#!/usr/bin/env python3

## HAIKU
# syllables: 5-7-5

from functools import wraps
import json
import random

from syllables import count_syllables


def get_lyrics():
    with open('../data/beatles_lyrics.json', 'r') as f:
        lyrics = json.loads(f.read())
    return [' '.join(song['lyrics']) for song in lyrics.values()]


def get_craigslist():
    with open('../data/craigslist.txt', 'r') as f:
        text = f.read()
    return [text]


def get_sonnets():
    with open('../data/shakespeare_sonnets.json', 'r') as f:
        sonnets = json.loads(f.read())
    return [sonnet for sonnet in sonnets.values()]


def build_corpus(data):
    d = {}

    for text in data:
        words = [word.strip('.,()-?!":').lower() for word in text.split() if word.strip('.,()-?!":')]
        for i, word in enumerate(words[:-1]):
            if not word in d:
                d[word] = []
            d[word].append(words[i+1])

    return d


def generate_line(word, num_syllables, d):
    words = find_with_backtrack(word, num_syllables, d)
    if words is None:
        #print('Could not find a line with', word)
        return None
    return ' '.join(words)


def find_with_backtrack(word, num_syllables, d):
    word_syllables = count_syllables(word)
    if word_syllables == num_syllables:
        # success!
        return [word]
    if word_syllables > num_syllables:
        return None

    remaining_syllables = num_syllables - word_syllables
    options = set([w for w in d[word] if count_syllables(w) <= remaining_syllables])
    if not options:
        # failure!
        return None

    # otherwise, we need to keep looking
    options = list(options)
    random.shuffle(options)
    for option in options:
        rest = find_with_backtrack(option, remaining_syllables, d)
        if rest is not None:
            # a good way to debug
            #print(' '.join([word] + rest))
            return [word] + rest

    # whoops
    return None


def try_generate_line(num_syllables, d):
    line = None
    while line is None:
        line = generate_line(random.choice(list(d.keys())), num_syllables, d)
    return line


def generate_haiku(d):
    # start by picking 7 pairs of rhyming words
    # then generate backwards for the right number of syllables
    haiku = []

    haiku.append(try_generate_line(5, d))
    haiku.append(try_generate_line(7, d))
    haiku.append(try_generate_line(5, d))

    return haiku


def main():
    #data = get_craigslist()
    #data = get_lyrics()
    data = get_sonnets()
    d = build_corpus(data)
    haiku = generate_haiku(d)
    print('\n'.join(haiku))


if __name__ == '__main__':
    main()
