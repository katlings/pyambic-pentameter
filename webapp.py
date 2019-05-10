from flask import Flask, render_template, request
app = Flask(__name__)
app.config.update(WTF_CSRF_ENABLED=False)

import random

from forms import GeneratePoemForm
from generate import text_sources, poem_styles


@app.route('/', methods=['GET', 'POST'])
def generate_page():
    form = GeneratePoemForm()
    print(form.validate())
    print(form.errors)

    if form.validate_on_submit():
        d, rev_d, seeds = text_sources[form.source.data]
        generate = poem_styles[form.style.data]
    else:
        source = random.choice(list(text_sources.keys()))
        form.source.data = source
        d, rev_d, seeds = text_sources[source]
        style = random.choice(list(poem_styles.keys()))
        generate = poem_styles[style]
        form.style.data = style

    poem = generate(d=d, rev_d=rev_d, seeds=seeds)
    print(poem)
    return render_template('generate.html', form=form, poem=poem)
