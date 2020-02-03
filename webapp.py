import logging
from logging.handlers import RotatingFileHandler
import random
import re

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectField

from .generate.generator import PoemMaker

pm = PoemMaker()
pm.setup()

app = Flask(__name__)
app.config.update(WTF_CSRF_ENABLED=False)

handler = RotatingFileHandler('poems.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)


def alphanum(s):
    return re.sub(r'[^a-z]+', '', s.lower())


class GeneratePoemForm(FlaskForm):
    source = SelectField('Source', choices=[(k, k) for k in pm.text_sources.keys()])
    style = SelectField('Style', choices=[(k, k) for k in pm.poem_styles.keys()])


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
        source = form.source.data
        style = form.style.data
    else:
        try:
            source_ask = request.args.get('source') or request.args.get('style')
            source_param = valid_param(source_ask, pm.text_sources)
            if source_param is not None:
                source = source_param
            else:
                source = random.choice(list(pm.text_sources.keys()))
            form.source.data = source

            style_ask = request.args.get('poem') or request.args.get('style')
            style_param = valid_param(style_ask, pm.poem_styles)
            if style_param is not None:
                style = style_param
            else:
                style = random.choice(list(pm.poem_styles.keys()))
            form.style.data = style
        except:
            app.logger.exception('Failed to select source and style')

    poem = pm.generate(source, style)
    app.logger.info(poem)
    print(poem)
    return render_template('generate.html', form=form, poem=poem)


if __name__ == '__main__':
    app.run()
