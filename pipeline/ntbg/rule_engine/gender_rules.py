from charsplit import splitter, Splitter

from pipeline.correction.pron_art.select_pron_form import get_possible_pronomen_lists_for_tag
from loguru import logger

from pipeline.spacy_shared.wordlib import follow_child_dep, follow_parent_dep, follow_child_dep_single_or_none, \
    follow_parent_dep_recursive
from wiktionary.db_extender import find_in_db_and_convert
from wiktionary.fnf import feminine_noun_forms, find_in_db

EIGENNAME_GEFUNDEN = 1
NO_FEMININE_FORM = 6

NOUN_KERNEL_NAME_FOUND = 2
KOPULA_SENTENCE = 3
APPOSITION = 4
GENITIVE_ATTRIBUTE = 5
RELATIVE_CLAUSE = 7
COREF_CHAIN = 8

BOTH_FORMS = 9

def _feminine_noun_forms(word):
    fnf = feminine_noun_forms(word, False)
    if fnf:
        return fnf
    else:
        fnf = feminine_noun_forms(word, True)

        if fnf:
            return fnf
        else:
            splits = splitter.split_compound(word.text)

            logger.debug(f"splits found: {splits}")

            if splits:
                fnf = feminine_noun_forms(splits[0][-1], True)
                return fnf

    return []


def _has_feminine_noun_form(word):
    return _feminine_noun_forms(word)

class GenderRule:
    def apply(self, doc, word, check_coref=True):
        raise NotImplementedError("apply() must be implemented by subclasses")

class ProperNameRule(GenderRule):
    def apply(self, doc, word, check_coref=True):
        if word.pos_ == "PROPN":
            return False, [("EIGENNAME_GEFUNDEN", f"Eigenname gefunden: {word}")]
        return True, None

def has_feminine_form(word):
    if word.pos_ == "NOUN":
        if not _has_feminine_noun_form(word):
            return False, [(NO_FEMININE_FORM, f"Keine feminine Wortform gefunden: {word}")]