from flask import Flask, render_template, request
app = Flask(__name__)
app.config.update(WTF_CSRF_ENABLED=False)

import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('poems.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

import random

from forms import GeneratePoemForm
from generate import text_sources, poem_styles
from tools.analyze import alphanum


@app.route('/', methods=['GET', 'POST'])
def generate_page():
    def valid_param(param, d):
        if param is not None:
            for k in d.keys():
                if alphanum(param) == alphanum(k):
                    return k

    form = GeneratePoemForm()

    app.logger.debug(form.validate())
    if form.errors:
        app.logger.warning(form.errors)

    if form.validate_on_submit():
        d, rev_d, seeds = text_sources[form.source.data]
        generate = poem_styles[form.style.data]
    else:
        try:
            source_ask = request.args.get('source') or request.args.get('style')
            source_param = valid_param(source_ask, text_sources)
            if source_param is not None:
                source = source_param
            else:
                source = random.choice(list(text_sources.keys()))
            form.source.data = source
            d, rev_d, seeds = text_sources[source]

            style_ask = request.args.get('poem') or request.args.get('style')
            style_param = valid_param(style_ask, poem_styles)
            if style_param is not None:
                style = style_param
            else:
                style = random.choice(list(poem_styles.keys()))
            generate = poem_styles[style]
            form.style.data = style
        except:
            app.logger.info('what the hell')
            app.logger.error('shit')
            app.logger.exception('shit')

    poem = generate(d=d, rev_d=rev_d, seeds=seeds)
    app.logger.info(poem)
    print(poem)
    return render_template('generate.html', form=form, poem=poem)


if __name__ == '__main__':
    app.run()
