from pipeline.correction.verb.change_verb_form import change_verb_form
from pipeline.spacy_shared._spacy import spacify
from wiktionary.api import find_verb_by_title


def test_change_verb_form():
    doc = spacify("Der Schüler geht ein Eis essen.")

    res = change_verb_form(doc[2], "Plur")

    assert res == "gehen"


