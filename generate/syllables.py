#!/usr/bin/env python3

from functools import wraps
import logging
import re

from nltk.corpus import cmudict
from num2words import num2words
d = cmudict.dict()


def clean_word(s):
    # we are actually gonna leave internal 's in for contraction purposes and
    # _s and .s in for "pronouncing code" purposes, as well as numbers
    return re.sub(r"[^a-z0-9\-_\.']+", '', s.lower().strip("'"))


def count_vowel_groups(word):
    # this is a first order approximation of number of syllables.
    # it won't be correct on  e.g. aria, Julia, praying, antiestablishment
    if not word:
        return 0

    vowels = 'aeiouy'
    digits = '0123456789'

    # special case for all numbers
    if all(letter in digits for letter in word):
        return count_syllables(num2words(word))

    # special case for no vowels - maybe it's an acronym. we can say each
    # letter individually and they're probably all one syllable (except w)
    if all(vowel not in word for vowel in vowels):
        return len(word) + 2 * word.count('w') + word.count('7') + word.count('0')

    syllables = 0
    last_seen_consonant = True
    for letter in word:
        if letter in digits:
            # just say the number
            syllables += 2 if letter in '07' else 1
            last_seen_consonant = True
        if letter not in vowels:
            last_seen_consonant = True
        else:
            syllables += last_seen_consonant
            last_seen_consonant = False

    # special case for last silent e
    # it's not quite worth special casing -ed
    if len(word) >= 2 and word[-1] == 'e' and word[-2] not in vowels:
        syllables -= 1

    return syllables


def count_syllables(word):
    if ' ' in word:
        return sum([count_syllables(w) for w in word.split()])

    # if we're looking at, say, a snake case variable name
    if '_' in word:
        return sum([count_syllables(w) for w in word.split('_')])

    # or if it's hyphenated
    if '-' in word:
        return sum([count_syllables(w) for w in word.split('-')])

    # or some other code stuff. we'll probably be pronouncing the . as 'dot'
    if '.' in word:
        return sum([count_syllables(w) for w in word.split('.')]) + len(word.split('.')) - 1

    if not word in d:
        return count_vowel_groups(word)

    sounds = d[word][0]
    syllables = 0
    for s in sounds:
        if '0' in s or '1' in s or '2' in s:
            syllables += 1
    return syllables


def get_syllable_stress(word):
    ends_with_ing = word.endswith("in'")
    word = clean_word(word)
    stresses_options = set()

    # special case for e.g. singin', prayin'. a common transcription in written lyrics
    # does not work on goin' as goin is apparently a word. hope the apostrophe is there
    if ends_with_ing or (not word in d and word.endswith('in') and word + 'g' in d):
        word = word + 'g'

    if not word in d:
        syllables = count_syllables(word)
        # return '000' and '111' so it fingerprints to 'xxx'
        stresses_options.add('0'*syllables)
        stresses_options.add('1'*syllables)
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


def syllable_fingerprint(word):
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
        fps.append(syllable_fingerprint(word))
    return ''.join(fps)


def rhyme_fingerprint(word):
    word = word.lower()
    if not word in d:
        return None

    # for now, just grab the last vowel sound and whatever occurs after it
    # then we can worry about slant rhymes and multisyllable rhymes and shit later
    # and also multiple pronunciations
    sounds = d[word][0]
    fingerprint = []

    for sound in sounds[::-1]:
        fingerprint.append(sound)
        # digits designate emphasis in syllables; we've found a syllable,
        # more or less
        if '0' in sound or '1' in sound or '2' in sound:
            break
        
    return tuple(fingerprint[::-1])


def syllables_match(a, b):
    return a == 'x' or b == 'x' or a == b


def scansion_matches(a, b):
    return len(a) == len(b) and all(syllables_match(a[i], b[i]) for i in range(len(a)))


def fulfills_scansion(word, desired_fp):
    syl_fp = syllable_fingerprint(word)
    return len(syl_fp) == len(desired_fp) and scansion_matches(syl_fp, desired_fp)


def valid_option(word, desired_fp):
    syl_fp = syllable_fingerprint(word)
    return len(syl_fp) <= len(desired_fp) and scansion_matches(syl_fp, desired_fp[-len(syl_fp):])


def remaining_scheme(word, remaining_syl):
    syl_fp = syllable_fingerprint(word)
    return remaining_syl[:-len(syl_fp)]


def potentially_iambic(word, ends_on_stress):
    syl_fp = syllable_fingerprint(word)
    if ends_on_stress:
        iamb_fp = '01' * (len(syl_fp)//2)
        if len(syl_fp) % 2 == 1:
            iamb_fp = '1' + iamb_fp
    else:
        iamb_fp = '10' * (len(syl_fp)//2)
        if len(syl_fp) % 2 == 1:
            iamb_fp = '0' + iamb_fp

    return scansion_matches(syl_fp, iamb_fp)


def potential_iambic_seed(word):
    return potentially_iambic(word, True)
