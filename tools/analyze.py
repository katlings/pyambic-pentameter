#!/usr/bin/env python3

from functools import wraps
import logging
import re

import click
from nltk.corpus import cmudict
d = cmudict.dict()


def alphanum(s):
    return re.sub(r'[^a-z]+', '', s.lower())


def count_vowel_groups(word):
    # this is a first order approximation of number of syllables.
    # it won't be correct on  e.g. aria, Julia, praying, antiestablishment
    vowels = 'aeiouy'
    syllables = 0
    last_seen_consonant = True
    for letter in word:
        if letter not in vowels:
            last_seen_consonant = True
        else:
            syllables += last_seen_consonant
            last_seen_consonant = False
    # special case for last silent e
    if len(word) >= 2 and word[-1] == 'e' and word[-2] not in vowels:
        syllables -= 1
    return syllables


def get_syllable_stress(word):
    ends_with_ing = word.endswith("in'")
    word = alphanum(word)
    stresses_options = set()

    # special case for e.g. singin', prayin'. a common transcription in written lyrics
    # does not work on goin' as goin is apparently a word. hope the apostrophe is there
    if ends_with_ing or (not word in d and word.endswith('in') and word + 'g' in d):
        word = word + 'g'

    if not word in d:
        # try all combinations of syllables. why not?
        # this will just fingerprint to 'xxxx' anyway though.
        syllables = count_vowel_groups(word)
        for i in range(2**syllables):
            pattern = format(i, 'b').zfill(syllables)
            if pattern == '11' or not '11' in pattern:  # filter out two stresses in a row - it's rare at best
                stresses_options.add(pattern)
    else:
        pronunciations = d[word]
        for p in pronunciations:
            stress = []
            for syllable in p:
                if '1' in syllable or '2' in syllable:  # for now, ignore whatever 2 means
                    stress.append('1')
                if '0' in syllable:
                    stress.append('0')  # todo: watch for two unstressed in a row
                                        # ^ wtf self, what does this mean
            stresses_options.add(''.join(stress))

    return stresses_options


# def fingerprint_different_lengths(stresses):
#     syllables = len(list(stresses)[0])
#    for syllable in syllables:


def fingerprint(word):
    stresses = get_syllable_stress(word)
    if not stresses:
        raise ValueError(f'Found no options for word {word}')
    if len(stresses) == 1:
        return stresses.pop()
    syllables = len(list(stresses)[0])
    if not all(len(s) == syllables for s in stresses):
        logging.debug('well crud we have to deal with multiple syllables here')
        logging.debug('%s, %s', word, stresses)
        return stresses.pop()  # lol pick one. TODO
    fp = []
    for i in range(syllables):
        if all(s[i] == '1' for s in stresses):
            fp.append('1')
        elif all(s[i] == '0' for s in stresses):
            fp.append('0')
        else:
            fp.append('x')
    return ''.join(fp)


def get_sequence_fingerprint(sequence):
    words = sequence.split()
    fps = []
    for word in words:
        fps.append(fingerprint(word))
    return ''.join(fps)


def memoize(f):
    cache = {}

    @wraps(f)
    def retrieve_or_store(a, b, *args, **kwargs):
        if not (a, b) in cache:
            cache[(a, b)] = f(a, b)
        return cache[(a, b)]

    return retrieve_or_store


@memoize
def edit_distance(a, b, f=None):
    if not a:
        return len(b)
    if not b:
        return len(a)
    if (f and f(a[0], b[0])) or (f is None and a[0] == b[0]):
        return edit_distance(a[1:], b[1:])

    return 1 + min(edit_distance(a, b[1:]), edit_distance(a[1:], b))


def syllables_match(a, b):
    return a == 'x' or b == 'x' or a == b


# hash a bunch of lyrics into line/stanza fingerprints and use that to fetch similar ones
# keyword: similar - some fudge factor will almost certainly be essential
# it may work to be more generous on one-syllable stressing
# take out parentheticals in lyric lines?


# build a db of hash: lyric and use to fetch similar lines
# what about entire stanzas?


@click.command()
@click.option('--verbose', '-v', count=True, help='Print debug information')
@click.argument('filename')
def main(verbose, filename):
    if verbose >= 1:
        logging.basicConfig(level=logging.DEBUG)

    try:
        with open(filename) as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = [filename]

    for line in lines:
        print(get_sequence_fingerprint(line))


if __name__ == '__main__':
    main()
