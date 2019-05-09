#!/usr/bin/env python3

import json
import os
import re

from bs4 import BeautifulSoup
from urllib import request

from collect_lyrics import LYRICS_FILE_PATH, fetch_page, scrape_and_save_lyrics

METADATA_URL = 'http://en.wikipedia.org/w/api.php?format=json&titles=List_of_songs_recorded_by_the_Beatles&action=query&prop=revisions&rvprop=content'


def song_title_key(song_title):
  return re.sub('\W+', '', song_title).lower()

def wiki_link_clean(my_string):
  my_string = my_string.strip()
  link = re.match('\[\[(.*)\]\]', my_string)
  if not link:
    return my_string
  link_title = re.match('.*\|(.*)', link.group(1))
  if not link_title:
    return link.group(1)
  else:
    return link_title.group(1)

def parse_metadata(metadata_json):
  md = json.loads(metadata_json.decode())['query']['pages']['6771955']['revisions'][0]['*']  # ugh

  all_songs = []

  # example = {{The Beatles list of songs row |anchor=Y |song=[[Yellow Submarine (song)|Yellow Submarine]] |year=1966 |album=[[Revolver (Beatles album)|Revolver]] |writer=McCartney, with Lennon |lead=Starkey |uk=1 |us=2 |notes=Nothing to speak of}}
  line_re = re.compile('^{{The Beatles list of songs row.*\|song=(.*)\|year=(.*)\|album=(.*)\|writer=(.*)\|lead=(.*?)[\||}]')

  lines = md.split('\n')
  for line in lines:
    match = line_re.match(line)
    if match:
      title, year, album, writer, lead = [wiki_link_clean(m) for m in match.group(1,2,3,4,5)]
      all_songs.append(dict(title=title, year=year, album=album, writer=writer, lead=lead))

  return sorted(all_songs, key=lambda s: s['title'])

def merge_data(lyrics_data, metadata):
  song_titles = {}
  for song in lyrics_data.keys():
    song_titles[song_title_key(song)] = song

  # hardcoding the mismatches, yay. map wiki key to key we already have. D:
  exceptions = {
    'annagotohim': 'anna',
    'digapony': 'idigapony',
    'dizzymisslizzy': 'dizzymisslizzie',
    'goldenslumbers': 'goldenslumberscarrythatweighttheend',
    'iwanttoholdyourhand': 'iwannaholdyourhand',
    'norwegianwoodthisbirdhasflown': 'norwegianwood',
    'moneythatswhatiwant': 'money',
    'revolution': 'revolution1revolution',
    'theballadofjohnandyoko': 'balladofjohnyoko',
    'youregoingtolosethatgirl': 'youregonnalosethatgirl',
    'youvereallygotaholdonme': 'youreallygotaholdonme'
  }

  for md_dict in metadata:
    key = song_title_key(md_dict['title'])

    if key in exceptions:
      key = exceptions[key]

    if key in song_titles:
      song = song_titles[key]
      lyrics_data[song].update(md_dict)

  return lyrics_data

def verify(songs_data):
  keys = ['lyrics', 'artist', 'year', 'album', 'writer', 'lead']
  for song in songs_data:
    for key in keys:
      if not key in songs_data[song]:
        print("Song %s does not have key %s" % (song, key))

def scrape_and_save_metadata():
  if not os.path.exists(LYRICS_FILE_PATH):
    scrape_and_save_lyrics()

  with open(LYRICS_FILE_PATH, 'r') as f:
    lyrics_data = json.load(f)

  metadata_json = fetch_page(METADATA_URL)
  metadata = parse_metadata(metadata_json)
  songs_data = merge_data(lyrics_data, metadata)

  # verify(songs_data)

  with open(LYRICS_FILE_PATH, 'w') as f:
    json.dump(songs_data, f)

if __name__ == '__main__':
  scrape_and_save_metadata()
