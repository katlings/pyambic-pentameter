import os

from .poems import (build_models, get_file, generate_haiku, generate_limerick,
                            generate_raven_verse, generate_sonnet)

DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class PoemMaker:
    def __init__(self, data_folder=DATA_FOLDER):
        self.data_folder = data_folder
        self.text_sources = {}
        self.poem_styles = {}
        self.set_up = False

    def setup(self):
        texts = os.listdir(DATA_FOLDER)

        for filename in texts:
            # strip '.txt' from filename for the string key
            lines = get_file
            self.text_sources[filename[:-4]] = build_models(get_file(os.path.join(DATA_FOLDER, filename)))

        self.poem_styles['haiku'] = generate_haiku
        self.poem_styles['limerick'] = generate_limerick
        self.poem_styles['raven_verse'] = generate_raven_verse
        self.poem_styles['sonnet'] = generate_sonnet

        self.set_up = True

    def generate(self, source, style):
        if not self.set_up:
            return 'Please run setup() first to initialize models'
        if source not in self.text_sources:
            return f'Source not found: {source}. Valid choices are {", ".join(self.text_sources)}'
        if style not in self.poem_styles:
            return f'Style not found: {style}. Valid choices are {", ".join(self.poem_styles)}'

        d, rev_d, seeds = self.text_sources[source]
        return '\n'.join(self.poem_styles[style](d=d, rev_d=rev_d, seeds=seeds))
