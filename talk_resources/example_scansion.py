from generate.syllables import syllable_fingerprint, scansion_matches
from generate.generator import PoemMaker
import random

pm = PoemMaker()
pm.setup()

d, rev_d, seeds = pm.text_sources['poem']

def valid(words, desired_meter):
    fps = ''.join([syllable_fingerprint(word) for word in words])
    return len(fps) <= len(desired_meter) and scansion_matches(fps, desired_meter[:len(fps)])

def all_done(words, pattern):
    fps = [syllable_fingerprint(word) for word in words]
    return scansion_matches(''.join(fps), pattern)

def generate_scansion_with_backtrack(d, pattern, words):
    if all_done(words, pattern):
        print(' '.join(words))
        return words
    if not valid(words, pattern):
        print(' '.join(words), 'X')
        return None

    print(' '.join(words))
    if not words:
        options = list(d.keys())
    else:
        last_word = words[-1]
        options = d[last_word]

    options = list(set(options))
    random.shuffle(options)
    for option in options:
        result = generate_scansion_with_backtrack(d, pattern, words + [option])
        if result is not None:
            return result


import random
