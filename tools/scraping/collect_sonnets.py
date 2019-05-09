#!/usr/bin/env python3

import json
import os

from bs4 import BeautifulSoup
import requests

BASE_URL = 'http://shakespeare.mit.edu/Poetry/'
INDEX_PAGE = 'sonnets.html'

LYRICS_FILE_PATH = os.path.join('..', 'data', 'shakespeare_sonnets.json')

def fetch_page(page):
    response = requests.get(page)
    return response.text

def parse_sonnet_links(sonnet_index_html):
    bs = BeautifulSoup(sonnet_index_html)  # actually it's anything but bs
    sonnets = [link.get('href') for link in bs.find_all('a') if link.string and link.get('href').startswith('sonnet')]
    return sorted(sonnets)

def clean(my_string):  # \uffffuck unicode apostrophes. this function took as long as the rest of the file put together
    return my_string.replace(u'\u2019', "'").encode('ascii', 'ignore').decode('ascii')

def parse_sonnet(sonnet_html):
    bs = BeautifulSoup(sonnet_html)
    sonnet_num = bs.find('title') 
    sonnet_quote = bs.find('blockquote')
    return sonnet_num.get_text(), sonnet_quote.get_text()

def get_sonnets(sonnet_link_list):
    all_sonnets = {}

    for page in sonnet_link_list:
        sonnet_html = fetch_page(BASE_URL + page)
        number, sonnet = parse_sonnet(sonnet_html)

        all_sonnets[number] = sonnet

    return all_sonnets

def scrape_and_save_sonnets():
    sonnet_index_html = fetch_page(BASE_URL + INDEX_PAGE)
    sonnet_link_list = parse_sonnet_links(sonnet_index_html)
    sonnets = get_sonnets(sonnet_link_list)

    with open(LYRICS_FILE_PATH, 'w') as f:
        json.dump(sonnets, f)

if __name__ == '__main__':
    scrape_and_save_sonnets()
