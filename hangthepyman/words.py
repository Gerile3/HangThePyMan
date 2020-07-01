from random import choice


def internet_check():
    # TODO
    pass


def daily_word():
    # TODO
    pass


def local_word(word=""):
    words = ["PYTHON", "GAME", "DEVELOP", "STEAM", "FLY"]
    if word:
        return word
    else:
        return choice(words)


def random_word():
    # TODO
    pass
