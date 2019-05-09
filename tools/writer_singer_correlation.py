#!/usr/bin/env python3

import json
import os
import re

DATA_FILE = os.path.join('..', 'data', 'beatles_lyrics.json')
BEATLES = ['Lennon', 'McCartney', 'Harrison', 'Starkey']


def load_data():
  with open(DATA_FILE, 'r') as f:
    data = json.load(f)
  return data

def person_of_interest(people):
  return re.sub('\W+', '', people.split(' ')[0].split(',')[0])

def compare_leads_and_writers():
  data = load_data()

  matches = []
  mismatches = []
  not_beatles = []

  for song, info in data.items():
    if not 'writer' in info or not 'lead' in info:
      continue
    writer = info['writer']
    lead = info['lead']

    if person_of_interest(writer) == person_of_interest(lead):
      # print("Match: %s, penned by %s, sung by %s" % (song, writer, lead))
      matches.append(song)
    else:
      # print("Nope! %s, penned by %s, sung by %s" % (song, writer, lead))
      mismatches.append(song)
      if person_of_interest(writer) not in BEATLES:
        # print("But, not written by a Beatle")
        not_beatles.append(song)
      # else:
      #   print("Nope! %s, penned by %s, sung by %s" % (song, writer, lead))

  num_matched = len(matches)
  num_mismatched = len(mismatches)
  num_songs = num_matched + num_mismatched  # would be the number of keys in data, but some are skipped
  num_not_beatles = len(not_beatles)
  percent_beatles = 1.0 * (num_songs - num_not_beatles) / num_songs * 100
  percent_matched = 1.0 * num_matched / num_songs * 100
  percent_matched_beatles = 1.0 * num_matched / (num_songs - num_not_beatles) * 100

  print(num_matched, "singer-writer matches")
  print(num_mismatched, "singer-writer mismatches")
  print(percent_beatles, "percent of songs written by a Beatle")
  print(percent_matched, "percent of songs sung by writer")
  print(percent_matched_beatles, "percent of Beatles songs sung by writer")
  print("   Exceptions:", [s for s in mismatches if not s in not_beatles])

if __name__ == '__main__':
  compare_leads_and_writers()
