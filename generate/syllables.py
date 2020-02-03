#!/usr/bin/env python3

from functools import wraps
import logging
import re

from nltk.corpus import cmudict
from num2words import num2words
d = cmudict.dict()


def clean_word(s):
    """
    Strip out selected punctuation and convert word to lower case, to normalize
    it in preparation for looking it up in the pronunciation dictionary
    """
    # we are actually gonna leave internal 's in for contraction purposes and
    # _s and .s in for "pronouncing code" purposes, as well as numbers
    return re.sub(r"[^a-z0-9\-_\.']+", '', s.lower().strip("'"))


def count_vowel_groups(word):
    """
    Iterate through the word to make a guess at how many syllables it has,
    based on the number of groupings of adjacent vowels.

    Includes some special cases to try to intelligently pronounce silent e,
    digits, single letters, words with no vowels that might be acronyms, etc.

    It won't be correct on words with adjacent vowels pronounced as different
    syllables e.g. aria, Julia, praying, antiestablishment
    """
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
        # add extra syllables for w, 7, 0
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
    """
    Make a best guess at the number of syllables in the word, using the
    pronunciation dictionary if available or the vowel groups approximation if
    not.
    """
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

    sounds = d[word][0]  # just pick the first pronunciation if there are multiple
    syllables = 0
    for s in sounds:
        if '0' in s or '1' in s or '2' in s:
            syllables += 1
    return syllables


def get_syllable_stress(word):
    """
    Get all possible syllable stress options, represented as a list of strings
    of 0 (unstressed), 1 (primary stress), and 2 (secondary stress)
    """
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
                if '1' in syllable:
                    stress.append('1')
                if '2' in syllable:  # secondary stress
                    stress.append('2')
                if '0' in syllable:
                    stress.append('0')
            stresses_options.add(''.join(stress))

    return stresses_options


def syllable_fingerprint(word):
    """
    Use the pronuncation dict to map the potential syllable stress patterns
    of a word to a ternary string "fingerprint"

    0 is a syllable that must be unstressed
    1 is a syllable that must be stressed
    x is a syllable that may be stressed or unstressed

    e.g. python => 10
    pronunciation => 0x010
    """
    stresses = get_syllable_stress(word)
    if not stresses:
        raise ValueError(f'Found no options for word {word}')
    if len(stresses) == 1:
        return stresses.pop()
    syllables = len(list(stresses)[0])
    if not all(len(s) == syllables for s in stresses):
        logging.debug('Multiple syllables found')
        logging.debug('%s, %s', word, stresses)
        return stresses.pop()  # lol just pick one. TODO
    fp = []
    for i in range(syllables):
        if all(s[i] == '1' for s in stresses):
            fp.append('1')
        elif all(s[i] == '0' for s in stresses):
            fp.append('0')
        else:
            fp.append('x')
    return ''.join(fp)


def rhyme_fingerprint(word):
    """
    Return a representation of the pronunciation of the last set of sounds in
    the word, starting at the last emphasized syllable

    In other words, return the sound that this word ends with, in order to find
    words that rhyme
    """
    word = word.lower()
    if not word in d:
        return None

    # for now, just grab the last vowel sound and whatever occurs after it
    # then we can worry about slant rhymes and multisyllable rhymes and shit later
    # and also multiple pronunciations
    sounds = d[word][0]
    fingerprint = []

    # there's probably a way to do this with list.find() or something
    for sound in sounds[::-1]:
        fingerprint.append(sound)
        # digits designate emphasis in syllables; we've found a syllable,
        # more or less
        if '1' in sound or '2' in sound:
            break
        
    return tuple(fingerprint[::-1])


def syllables_match(a, b):
    return a == 'x' or b == 'x' or a == b


def scansion_matches(a, b):
    return len(a) == len(b) and all(syllables_match(a[i], b[i]) for i in range(len(a)))


def fulfills_scansion(word, desired_fp):
    """
    True if the word's meter and the desired meter are compatible
    """
    syl_fp = syllable_fingerprint(word)
    return scansion_matches(syl_fp, desired_fp)


def valid_option(word, desired_fp):
    """
    True if the word's meter is compatible at the end of the desired meter
    """
    syl_fp = syllable_fingerprint(word)
    return len(syl_fp) <= len(desired_fp) and scansion_matches(syl_fp, desired_fp[-len(syl_fp):])


def remaining_scheme(word, remaining_syl):
    """
    Cut off the word's length and return the remaining meter to look for
    """
    syl_fp = syllable_fingerprint(word)
    return remaining_syl[:-len(syl_fp)]
