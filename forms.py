from flask_wtf import FlaskForm
from wtforms import SelectField

from generate import text_sources, poem_styles


class GeneratePoemForm(FlaskForm):
    source = SelectField('Source', choices=[(k, k) for k in text_sources.keys()])
    style = SelectField('Style', choices=[(k, k) for k in poem_styles.keys()])
