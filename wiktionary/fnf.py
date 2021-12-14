import json

from utils.list import filter_none
from utils.string import remove_prefix
from wiktionary.api import find_by_title, find_by_any_form


def has_male_noun_form(word):
    return male_noun_forms(word) is not None

# ToDo: Umziehen?
def male_noun_forms(word):
    # Gibt es das Wort in unserer Wort-Datenbank?

    lemma = word
    if not isinstance(word, str):
        lemma = word.lemma_

    lemma_in_db = find_by_title(lemma)

    if not lemma_in_db:
        return None

    male_forms_in_db = lemma_in_db["maennliche_formen"]

    if not male_forms_in_db:
        return None

    male_forms = json.loads(male_forms_in_db)
    male_forms = [find_by_title(f) for f in male_forms]

    if not male_forms:
        return None

    return male_forms


def has_feminine_noun_form(word, search_every_form=False):
    return feminine_noun_forms(word, search_every_form) is not None

def find_in_db(word, search_every_form=False):
    # Gibt es das Wort in unserer Wort-Datenbank?

    lemma = word
    if not isinstance(word, str):
        lemma = word.lemma_

    if search_every_form:
        lemma_in_db = find_by_any_form(lemma)
    else:
        lemma_in_db = find_by_title(lemma)

    if not lemma_in_db:
        return None

    return lemma_in_db



def feminine_noun_forms(word, search_every_form=False):
    # Gibt es das Wort in unserer Wort-Datenbank?

    lemma = word
    if not isinstance(word, str):
        lemma = word.lemma_

    #
    # In einigen Satzkonstruktionen steht einem Nomen ein "-" voran. Dieses ist nicht zu berücksichtigen.
    # Bsp.: Wissenschaftlerinnen und -Wissenschaftler
    #
    lemma = remove_prefix(lemma, "-")

    if search_every_form:
        lemma_in_db = find_by_any_form(lemma)
    else:
        lemma_in_db = find_by_title(lemma)

    if not lemma_in_db:
        return None

    feminine_forms_in_db = lemma_in_db["weibliche_formen"]

    if not feminine_forms_in_db:
        return None

    feminine_forms = feminine_forms_in_db
    feminine_forms = filter_none([find_by_title(f) for f in feminine_forms])

    if not feminine_forms:
        return None

    return feminine_forms
