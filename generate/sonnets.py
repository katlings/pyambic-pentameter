#!/usr/bin/env python3

## SONNETS
# rhyme scheme: abab cdcd efef gg

from functools import wraps
import json
import random

import click

from syllables import rhyme_fingerprint, potential_iambic_seed, remaining_scheme, scansion_matches, valid_option, fulfills_scansion


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
    # data is a list of seed strings; each chunk of text may be unrelated (e.g. lyrics from different songs)
    d = {}
    word_set = set()

    # we are gonna build a backwards markov, so we can start with a rhyme and
    # fill in the lines from there
    for text in data:
        words = [word.strip('.,()-?!":').lower() for word in text.split() if word.strip('.,()-?!":')]
        word_set.update(words)
        words.reverse()

        for i, word in enumerate(words[:-1]):
            if not word in d:
                d[word] = []
            d[word].append(words[i+1])

    # we can seed off of words that are valid in iambic pentameter - that is, they
    # can end with a stressed syllable - and have at least one matching rhyme
    seeds = {}
    for word in word_set:
#       if not potential_iambic_seed(word):
#           continue
        rf = rhyme_fingerprint(word)
        if rf is None:
            continue
        if not rf in seeds:
            seeds[rf] = []
        seeds[rf].append(word)

    valid_seeds = {key:value for key, value in seeds.items() if len(value) >= 2}

    return d, valid_seeds


def find_with_backtrack(word, scansion_pattern, d):
    if fulfills_scansion(word, scansion_pattern):
        # success!
        return [word]
    if not valid_option(word, scansion_pattern):
        return None

    rest_pattern = remaining_scheme(word, scansion_pattern)
    options = set([w for w in d[word] if valid_option(w, rest_pattern)])
    if not options:
        # failure!
        return None

    # otherwise, we need to keep looking
    options = list(options)
    random.shuffle(options)
    for option in options:
        rest = find_with_backtrack(option, rest_pattern, d)
        if rest is not None:
            # a good way to debug
            #print(' '.join([word] + rest))
            return [word] + rest

    # whoops
    return None


def generate_pattern(seed_words, pattern, d, k=2):
    lines = []
    for seed in seed_words:
        line = find_with_backtrack(seed, pattern, d)
        if line is not None:
            lines.append(' '.join(line[::-1]))
        if len(lines) == k:
            return lines

    return None


def generate_iambic(seed_words, d, k=2, meter=5):
    return generate_pattern(seed_words, '01'*meter, d, k)


def generate_sonnet(d, seeds):
    # start by picking 7 pairs of rhyming words
    # then generate backwards for the right number of syllables

    sonnet = []

    while len(sonnet) < 14:
        rhyme_sound = random.choice(list(seeds.keys()))
        lines = generate_iambic(seeds[rhyme_sound], d)
        if lines is not None:
            sonnet.extend(lines)

    # now shuffle the lines so the rhyme scheme is right
    sonnet[1], sonnet[2] = sonnet[2], sonnet[1]
    sonnet[5], sonnet[6] = sonnet[6], sonnet[5]
    sonnet[9], sonnet[10] = sonnet[10], sonnet[9]
    
    sonnet.insert(4, '')
    sonnet.insert(9, '')
    sonnet.insert(14, '')

    return sonnet


def generate_limerick(d, seeds):
    # generate 3 of one pattern and 2 of another
    triplet = None
    while triplet is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        triplet = generate_pattern(seeds[rhyme_sound], '01101101', d, k=3)
    couplet = None
    while couplet is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        couplet = generate_pattern(seeds[rhyme_sound], '01101', d)

    limerick = triplet[:2] + couplet + [triplet[2]]

    return limerick


@click.command()
@click.argument('source')
@click.argument('poem')
def main(source, poem):
    data = None
    if source == 'craigslist':
        data = get_craigslist()
    elif source == 'beatles':
        data = get_lyrics()
    elif source == 'shakespeare':
        data = get_sonnets()
    if data is None:
        return

    d, seeds = build_corpus(data)

    if poem == 'sonnet':
        sonnet = '\n'.join(generate_sonnet(d, seeds))
        print(sonnet)
        return sonnet
    elif poem == 'limerick':
        limerick = '\n'.join(generate_limerick(d, seeds))
        print(limerick)
        return limerick



if __name__ == '__main__':
    main()
