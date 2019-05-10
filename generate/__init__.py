from .poems import (build_corpus, get_beatles, get_file, get_shakespeare,
                   generate_haiku, generate_limerick, generate_sonnet)

text_sources = {}

beatles_data = get_beatles('generate/data/beatles_lyrics.json')
text_sources['The Beatles'] = build_corpus(beatles_data)

craigslist_data = get_file('generate/data/craigslist.txt')
text_sources['Craigslist'] = build_corpus(craigslist_data)

hamilton_data = get_file('generate/data/hamilton-lyrics.txt')
text_sources['Hamilton'] = build_corpus(hamilton_data)

python_data = get_file('generate/data/python-docs.txt')
text_sources['Python Docs'] = build_corpus(python_data)

shakespeare_data = get_shakespeare('generate/data/shakespeare_sonnets.json')
text_sources['Shakespeare'] = build_corpus(shakespeare_data)


poem_styles = {}

poem_styles['haiku'] = generate_haiku
poem_styles['limerick'] = generate_limerick
poem_styles['sonnet'] = generate_sonnet
