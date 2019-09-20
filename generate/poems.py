#!/usr/bin/env python3

import json
import random

from .syllables import count_syllables, fulfills_scansion, remaining_scheme, rhyme_fingerprint, potential_iambic_seed, valid_option


def get_beatles(filepath):
    with open(filepath, 'r') as f:
        lyrics = json.loads(f.read())
    return [' '.join(song['lyrics']) for song in lyrics.values()]


def get_file(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    return [text]


def get_shakespeare(filepath):
    with open(filepath, 'r') as f:
        sonnets = json.loads(f.read())
    return [sonnet for sonnet in sonnets.values()]


def build_corpus(data):
    # data is a list of seed strings; each chunk of text may be unrelated (e.g. lyrics from different songs)
    d = {}
    reverse_d = {}
    word_set = set()

    for text in data:
        strip_chars = '.,()-?!":*'
        words = [word.strip(strip_chars).lower() for word in text.split() if word.strip(strip_chars)]
        word_set.update(words)

        for i, word in enumerate(words[:-1]):
            if not word in d:
                d[word] = []
            d[word].append(words[i+1])


        # we are also gonna build a backwards markov, so we can start with a rhyme and
        # fill in the lines from there
        words.reverse()

        for i, word in enumerate(words[:-1]):
            if not word in reverse_d:
                reverse_d[word] = []
            reverse_d[word].append(words[i+1])

    # we can seed off of words that have at least one matching rhyme
    seeds = {}
    for word in word_set:
        # we could reduce this set further by checking for the right stress for the
        # pattern, but iambic isn't necessarily the right one
#       if not potential_iambic_seed(word):
#           continue
        rf = rhyme_fingerprint(word)
        if rf is None:
            continue
        if not rf in seeds:
            seeds[rf] = []
        seeds[rf].append(word)

    rhyme_seeds = {key:value for key, value in seeds.items() if len(value) >= 2}

    return d, reverse_d, rhyme_seeds


def find_scansion_with_backtrack(word, scansion_pattern, d):
    if fulfills_scansion(word, scansion_pattern):
        # success!
        return [word]
    if not valid_option(word, scansion_pattern):
        return None

    rest_pattern = remaining_scheme(word, scansion_pattern)
    options = set([w for w in d.get(word, []) if valid_option(w, rest_pattern)])
    if not options:
        # failure!
        return None

    # otherwise, we need to keep looking
    options = list(options)
    random.shuffle(options)
    for option in options:
        rest = find_scansion_with_backtrack(option, rest_pattern, d)
        if rest is not None:
            # a good way to debug
            #print(' '.join([word] + rest))
            return [word] + rest

    # whoops
    return None


def find_syllables_with_backtrack(word, num_syllables, d):
    word_syllables = count_syllables(word)
    if word_syllables == num_syllables:
        # success!
        return [word]
    if word_syllables > num_syllables:
        return None

    remaining_syllables = num_syllables - word_syllables
    options = set([w for w in d.get(word, []) if count_syllables(w) <= remaining_syllables])
    if not options:
        # failure!
        return None

    options = list(options)
    random.shuffle(options)
    for option in options:
        rest = find_syllables_with_backtrack(option, remaining_syllables, d)
        if rest is not None:
            return [word] + rest

    return None


def generate_pattern(seed_words, pattern, d, k=2):
    lines = []
    for seed in seed_words:
        line = find_scansion_with_backtrack(seed, pattern, d)
        if line is not None:
            lines.append(' '.join(line[::-1]))
        if len(lines) == k:
            return lines

    return None


def generate_iambic(seed_words, d, k=2, meter=5):
    return generate_pattern(seed_words, '01'*meter, d, k)


def generate_syllables(num_syllables, d, preseed=None):
    line = None
    while line is None:
        if preseed is None:
            seed = random.choice(list(d.keys()))
        else:
            seed = random.choice(d.get(preseed, list(d.keys())))
        line = find_syllables_with_backtrack(seed, num_syllables, d)
    return ' '.join(line)


def generate_sonnet(rev_d, seeds, **kwargs):
    # start by picking 7 pairs of rhyming words
    # then generate backwards for the right number of syllables

    sonnet = []

    while len(sonnet) < 14:
        rhyme_sound = random.choice(list(seeds.keys()))
        lines = generate_iambic(seeds[rhyme_sound], rev_d)
        if lines is not None:
            sonnet.extend(lines)

    # now shuffle the lines so the rhyme scheme is right
    sonnet[1], sonnet[2] = sonnet[2], sonnet[1]
    sonnet[5], sonnet[6] = sonnet[6], sonnet[5]
    sonnet[9], sonnet[10] = sonnet[10], sonnet[9]
    
    # and add breaks between stanzas
    sonnet.insert(4, '')
    sonnet.insert(9, '')
    sonnet.insert(14, '')

    return sonnet


def generate_limerick(rev_d, seeds, **kwargs):
    # generate 3 of one pattern and 2 of another
    triplet = None
    while triplet is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        triplet = generate_pattern(seeds[rhyme_sound], '01101101', rev_d, k=3)
    couplet = None
    while couplet is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        couplet = generate_pattern(seeds[rhyme_sound], '01101', rev_d)

    limerick = triplet[:2] + couplet + [triplet[2]]

    return limerick


def generate_raven_verse(rev_d, seeds, **kwargs):
    """
    short1 short1
    long2x
    short3 short3
    short3 short2x
    long2x
    short2x
    """
    first_row = None
    while first_row is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        first_row = generate_pattern(seeds[rhyme_sound], '10101010', rev_d, k=2)
    intermediates = None
    while intermediates is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        intermediates = generate_pattern(seeds[rhyme_sound], '10101010', rev_d, k=3)
    longs = None
    shorts = None
    while longs is None or shorts is None:
        rhyme_sound = random.choice(list(seeds.keys()))
        longs = generate_pattern(seeds[rhyme_sound], '101010101010101', rev_d, k=2)
        random.shuffle(seeds[rhyme_sound])
        shorts = generate_pattern(seeds[rhyme_sound], '1010101', rev_d, k=2)
    print(first_row, intermediates, longs, shorts)

    verse = [first_row[0] + ' ' + first_row[1],
             longs[0],
             intermediates[0] + ' ' + intermediates[1],
             intermediates[2] + ' ' +  shorts[0],
             longs[1],
             shorts[1]]

    return verse


def generate_haiku(d, **kwargs):
    haiku = []

    haiku.append(generate_syllables(5, d))
    haiku.append(generate_syllables(7, d, preseed=haiku[-1].split()[-1]))
    haiku.append(generate_syllables(5, d, preseed=haiku[-1].split()[-1]))

    return haiku
