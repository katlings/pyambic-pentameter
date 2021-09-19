#!/usr/bin/env python3

import json
import random

from .syllables import count_syllables, fulfills_scansion, remaining_scheme, rhyme_fingerprint, valid_option


def get_file(filepath):
    '''
    Read a file and return a list of chunks of text, separated by paragraph
    breaks (two empty lines in a row).

    When making a Markov model from the output, text chunks will be considered
    separate (they will all go into the model, but the last word of one chunk
    will not be connected to the first word of the next).
    '''
    with open(filepath, 'r') as f:
        text = f.read()
    return text.split('\n\n')


def build_models(data):
    '''
    builds and returns a Markov dictionary, a reverse dictionary, and a set of
    rhymes from the input text

    data is a list of seed strings; each chunk of text may be unrelated (e.g.
    lyrics from different songs)
    '''
    d = {}
    reverse_d = {}
    word_set = set()

    for text in data:
        strip_chars = '.,()-?!":*;'
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


def generate_syllables(num_syllables, d, preseed=None):
    line = None
    while line is None:
        if preseed is None:
            seed = random.choice(list(d.keys()))
        else:
            seed = random.choice(d.get(preseed, list(d.keys())))
        line = find_syllables_with_backtrack(seed, num_syllables, d)
    return ' '.join(line)


def generate_haiku(d, **kwargs):
    haiku = []

    haiku.append(generate_syllables(5, d))
    haiku.append(generate_syllables(7, d, preseed=haiku[-1].split()[-1]))
    haiku.append(generate_syllables(5, d, preseed=haiku[-1].split()[-1]))

    return haiku


def generate_poem(pattern, definitions, rev_d, seeds, **kwargs):
    '''
    Build your own poem

    pattern: a string describing a rhyme pattern e.g., ABABCC. Use a space
        to indicate line breaks
    definitions: a dictionary with keys corresponding to each rhyme line e.g.
        'A' and values describing the syllable pattern e.g. '01101101'
    '''

    if not all(p in definitions for p in pattern if p != ' '):
        raise ValueError('Must define all rhymes used')

    # Generate the appropriate number of matching lines for each pattern
    distinct_rhymes = set(pattern)
    if ' ' in distinct_rhymes:
        distinct_rhymes.remove(' ')

    rhymes = {}

    for p in distinct_rhymes:
        rhyme = None
        while rhyme is None:
            rhyme_sound = random.choice(list(seeds.keys()))
            rhyme = generate_pattern(seeds[rhyme_sound], definitions[p], rev_d, k=pattern.count(p))
        rhymes[p] = rhyme

    # Assemble them
    output = []
    line_output = []

    for rhyme in pattern:
        if rhyme == ' ':
            output.append(' '.join(line_output))
            line_output = []
        else:
            line_output.append(rhymes[rhyme].pop())

    output.append(' '.join(line_output))

    return output


def generate_raven_verse(rev_d, seeds, **kwargs):
    segment = '10101010'
    segment_short  = '1010101'

    return generate_poem(
        'AA BC DD DC EC C',
        {
            'A': segment,
            'B': segment,
            'C': segment_short,
            'D': segment,
            'E': segment,
        },
        rev_d,
        seeds,
        **kwargs)


def generate_limerick(rev_d, seeds, **kwargs):
    return generate_poem(
        'A A B B A',
        {
            'A': '01001001',
            'B': '01001',
        },
        rev_d,
        seeds,
        **kwargs)


def generate_sonnet(rev_d, seeds, **kwargs):
    i_p = '01' * 5  # iambic pentameter

    return generate_poem(
        'A B A B  C D C D  E F E F  G G',
        {
            'A': i_p,
            'B': i_p,
            'C': i_p,
            'D': i_p,
            'E': i_p,
            'F': i_p,
            'G': i_p,
        },
        rev_d,
        seeds,
        **kwargs)
