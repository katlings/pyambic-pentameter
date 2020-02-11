pyambic-pentameter
========

A webapp that Markov-generates poems from plaintext.

------

Setup:

Drop plain text sources in `/generate/data/` as `SOURCE_NAME.txt`.

`pip install -r requirements.txt` (Virtualenv recommended.)

You will need to download the pronunciation dictionary once with `python -c "import nltk; nltk.download('cmudict')"` or you will get the runtime error `Resource cmudict not found.`

Run with `flask run`.

(May require some futzing with relative/absolute imports depending on setup.)

Browse to `http://localhost:5000` to read poems!
