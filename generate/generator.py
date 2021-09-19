from functools import lru_cache
import os

from .poems import (build_models, get_file, generate_haiku, generate_limerick,
                            generate_raven_verse, generate_sonnet, generate_common_meter)

DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class PoemMaker:
    def __init__(self, data_folder=DATA_FOLDER):
        self.data_folder = data_folder
        self.text_sources = {}
        self.poem_styles = {}
        self.set_up = False

    def setup(self):
        '''
        Run once before generating any poems to build Markov and rhyme models
        for every data source found in the given data folder
        '''
        texts = os.listdir(DATA_FOLDER)

        for filename in texts:
            if filename.startswith('.'):
                continue
            # strip '.txt' from filename for the string key
            self.text_sources[filename[:-4]] = build_models(get_file(os.path.join(DATA_FOLDER, filename)))

        self.poem_styles['haiku'] = generate_haiku
        self.poem_styles['limerick'] = generate_limerick
        self.poem_styles['raven verse'] = generate_raven_verse
        self.poem_styles['sonnet'] = generate_sonnet
        self.poem_styles['common meter'] = generate_common_meter

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

    # whoops - can't cache build_models because the input is an unhashable list
    # so give it a wrapper
    @lru_cache(maxsize=32)
    def build_custom_models(self, source_text):
        return build_models([source_text])

    def generate_custom(self, source_text, style):
        d, rev_d, seeds = self.build_custom_models(source_text)
        return '\n'.join(self.poem_styles[style](d=d, rev_d=rev_d, seeds=seeds))
