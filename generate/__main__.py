#!/usr/bin/env python3

import click

from .poems import (build_corpus,
                    get_beatles, get_file, get_shakespeare,
                    generate_haiku, generate_limerick, generate_sonnet)


@click.command()
@click.argument('source')
@click.argument('poem_type')
def main(source, poem_type):
    data = None
    if source == 'beatles':
        data = get_beatles('data/beatles_lyrics.json')
    elif source == 'craigslist':
        data = get_file('data/craigslist.txt')
    elif source == 'hamilton':
        data = get_file('data/hamilton-lyrics.txt')
    elif source == 'python':
        data = get_file('data/python-docs.txt')
    elif source == 'shakespeare':
        data = get_shakespeare('data/shakespeare_sonnets.json')
    if data is None:
        print('Valid sources are craigslist, beatles, python, shakespeare')
        return

    d, reverse_d, seeds = build_corpus(data)

    poem = None
    if poem_type == 'sonnet':
        poem = generate_sonnet(reverse_d, seeds)
    elif poem_type == 'limerick':
        poem = generate_limerick(reverse_d, seeds)
    elif poem_type == 'haiku':
        poem = generate_haiku(d)
    if poem is None:
        print ('Valid poem types are sonnet, limerick, haiku')
        return

    print(poem)
    return poem


if __name__ == '__main__':
    main()
