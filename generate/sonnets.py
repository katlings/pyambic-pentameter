#!/usr/bin/env python3

## SONNETS
# rhyme scheme: abab cdcd efef gg

import json
import random

from nltk.corpus import cmudict
rd = cmudict.dict()


def get_lyrics():
    with open('../data/beatles_lyrics.json', 'r') as f:
        lyrics = json.loads(f.read())
    return lyrics


def rhyme_fingerprint(word):
    word = word.lower()
    if not word in rd:
        return None

    # for now, just grab the last vowel sound and whatever occurs after it
    # then we can worry about slant rhymes and multisyllable rhymes and shit later
    # and also multiple pronunciations
    sounds = rd[word][0]
    fingerprint = []

    for sound in sounds[::-1]:
        fingerprint.append(sound)
        # digits designate emphasis in syllables; we've found a syllable,
        # more or less
        if '0' in sound or '1' in sound or '2' in sound:
            break
        
    return tuple(fingerprint[::-1])


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


def count_syllables(word):
    if not word in rd:
        return count_vowel_groups(word)
    sounds = rd[word][0]
    syllables = 0
    for s in sounds:
        if '0' in s or '1' in s or '2' in s:
            syllables += 1
    return syllables


def build_lyrics_corpus():
    d = {}
    data = get_lyrics()
    word_set = set()

    # we are gonna build a backwards markov, so we can start with a rhyme and
    # fill in the lines from there
    for song, song_data in data.items():
        lyrics = []
        for line in song_data['lyrics']:
            lyrics.extend(line.split())
        
        lyrics = [word.strip('.,()-').lower() for word in lyrics if word.strip('.,()-')]
        word_set.update(lyrics)
        lyrics.reverse()

        for i, word in enumerate(lyrics[:-1]):
            if not word in d:
                d[word] = []
            d[word].append(lyrics[i+1])

    rhymes = {}
    for word in word_set:
        rf = rhyme_fingerprint(word)
        if rf is None:
            continue
        if not rf in rhymes:
            rhymes[rf] = []
        rhymes[rf].append(word)

    multi_rhymes = {key:value for key, value in rhymes.items() if len(value) >= 2}

    return d, multi_rhymes


def generate_line(seed, d):
    line = []
    word = seed
    syllables = 0
    # we're looking for 10 syllables
    # TODO - iambic syllables !!!!!!
    # may involve backtrack
    while syllables < 10:
        syllables += count_syllables(word)
        line.append(word)
        word = random.choice(d[word])
    return ' '.join(line[::-1])


def generate_sonnet(d, rhymes):
    # start by picking 7 pairs of rhyming words
    # then generate backwards for the right number of syllables
    # then worry about emphasis later

    rhyme_sounds = random.sample(list(rhymes.keys()), 7)

    sonnet = []

    for rhyme in rhyme_sounds:
        seeds = random.sample(rhymes[rhyme], 2)
        for seed in seeds:
            sonnet.append(generate_line(seed, d))
    
    # now shuffle the lines so the rhyme scheme is right
    sonnet[1], sonnet[2] = sonnet[2], sonnet[1]
    sonnet[5], sonnet[6] = sonnet[6], sonnet[5]
    sonnet[9], sonnet[10] = sonnet[10], sonnet[9]

    return sonnet


def main():
    d, rhymes = build_lyrics_corpus()
    sonnet = generate_sonnet(d, rhymes)
    print('\n'.join(sonnet))


if __name__ == '__main__':
    main()
