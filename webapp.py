from flask import Flask
app = Flask(__name__)

from poems import (build_corpus,
                   get_beatles, get_craigslist, get_shakespeare,
                   generate_haiku, generate_limerick, generate_sonnet)

beatles_data = get_beatles('data/beatles_lyrics.json')
b_dict, b_revdict, b_seeds = build_corpus(beatles_data)

craigslist_data = get_craigslist('data/craigslist.txt')
c_dict, c_revdict, c_seeds = build_corpus(craigslist_data)

shakespeare_data = get_shakespeare('data/shakespeare_sonnets.json')
s_dict, s_revdict, s_seeds = build_corpus(shakespeare_data)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/generate')
def generate_page():
    'i want a <> in the style of <>'
    'again! | i want'
    return generate_limerick(b_revdict, b_seeds)
