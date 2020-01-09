import random


def build_model(source_text):
    list_of_words = source_text.split()
    model = {}

    for i, word in enumerate(list_of_words[:-1]):
        if not word in model:
            model[word] = []
        next_word = list_of_words[i+1]
        model[word].append(next_word)

    return model


def markov_generate(source_text, num_words=20):
    model = build_model(source_text)
    seed = random.choice(list(model.keys()))
    output = [seed]
    for i in range(num_words):
        last_word = output[-1]
        next_word = random.choice(model[last_word])
        output.append(next_word)
        if next_word not in model:
            break
    return ' '.join(output)
