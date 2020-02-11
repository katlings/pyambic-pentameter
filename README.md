pyambic-pentameter
========

A webapp that Markov-generates poems from plaintext.

------

Setup:

Drop plain text sources in `/generate/data/` as `SOURCE_NAME.txt`.

`pip install -r requirements.txt` (Virtualenv recommended.)

Run with `flask run`.

(May require some futzing with relative/absolute imports depending on setup.)

(You may need to `python -c "import nltk; nltk.download('cmudict')"` if you get the runtime error `Resource cmudict not found.`

Browse to `http://localhost:5000` to read poems!
