#!/usr/bin/env python3

import json
import random

from analyze import get_sequence_fingerprint


def get_lyrics():
    with open('../data/beatles_lyrics.json', 'r') as f:
        lyrics = json.loads(f.read())
    return lyrics


def main():
    lyrics = get_lyrics()
    song, data = random.choice(list(lyrics.items()))
    print(song)
    for line in data['lyrics']:
        print(get_sequence_fingerprint(line))


if __name__ == '__main__':
    main()
