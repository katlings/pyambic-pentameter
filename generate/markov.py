#!/usr/bin/env python3

import json
import random


def get_lyrics():
    with open('../data/beatles_lyrics.json', 'r') as f:
        lyrics = json.loads(f.read())
    return lyrics


def build_lyrics():
    d = {}
    data = get_lyrics()

    for song, song_data in data.items():
        lyrics = []
        for line in song_data['lyrics']:
            lyrics.extend(line.split())
        lyrics.append('EOS')
        
        lyrics = [word.strip(',()') for word in lyrics if word.strip(',()')]

        for i, word in enumerate(lyrics[:-1]):
            if not word in d:
                d[word] = []
            d[word].append(lyrics[i+1])

    return d


def generate_lyrics(d):
    starting_words = [word for word in d.keys() if word[0].isupper()]
    word = random.choice(starting_words)

    lyrics = []
    words = 0

    # average song is 170 words long; cap at 200
    while not (word == 'EOS' or words > 200):
        lyrics.append(word)
        word = random.choice(d[word])
        words += 1

    return ' '.join(lyrics)


def main():
    d = build_lyrics()
    print(generate_lyrics(d))


if __name__ == '__main__':
    main()
