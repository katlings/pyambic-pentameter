#!/usr/bin/env python3

import json
import os

from bs4 import BeautifulSoup
from urllib import request

BASE_URL = 'http://www.beatleslyrics.org/index_files/'
SONG_INDEX_PAGE = 'Page13763.htm'

def fetch_page(page):
  response = request.urlopen(BASE_URL + page)
  return response.read()

def parse_song_links(song_index_html):
  bs = BeautifulSoup(song_index_html)  # actually it's anything but bs
  songs = [link.get('href') for link in bs.find_all('a') if link.string and link.get('href').startswith('Page')]
  return sorted(songs)

def clean(my_string):  # \uffffuck unicode apostrophes. this function took as long as the rest of the file put together
  return my_string.replace(u'\u2019', "'").encode('ascii', 'ignore').decode('ascii')

def parse_lyrics(lyrics_html):
  bs = BeautifulSoup(lyrics_html)
  *_, lyrics_table = bs.find_all('table')
  title, artist, *lyrics = lyrics_table.stripped_strings
  return clean(title), clean(artist), [clean(l) for l in lyrics]

def get_lyrics(song_link_list):
  all_lyrics = {}

  for page in song_link_list:
    lyrics_html = fetch_page(page)
    title, artist, lyrics = parse_lyrics(lyrics_html)

    if title and lyrics:
      all_lyrics[title] = {}
      all_lyrics[title]['artist'] = artist
      all_lyrics[title]['lyrics'] = lyrics

  return all_lyrics

def run():
  song_index_html = fetch_page(SONG_INDEX_PAGE)
  song_link_list = parse_song_links(song_index_html)
  song_lyrics = get_lyrics(song_link_list)

  with open(os.path.join('..', 'data', 'beatles_lyrics.json'), 'w') as f:
    json.dump(song_lyrics, f)

if __name__ == '__main__':
  run()
