import loguru

from pipeline.correction.correction2 import generate_possible_corrections
from pipeline.initial_words.fiw import find_initial_words
from pipeline.ntbg.ntbg import needs_to_be_gendered
from pipeline.spacy_shared._spacy import spacify_with_coref
from pipeline.spacy_shared.wordlib import get_coref_words_in_sentence


def full_pipeline(text):
    loguru.logger.error(text)
    """
    Führt eine vollständige Analyse durch:
    1. Initiale spaCy-Analyse mit Koreferenz
    2. Suche nach maskulinen Formen
    3. Prüfung auf generisches Maskulinum
    4. Ggf. Generierung von Korrekturvorschlägen
    Rückgabe: Liste von Erkennungen mit Metadaten
    """
    result = []

    try:
        doc = spacify_with_coref(text)
    except Exception as e:
        loguru.logger.error("Fehler bei der spaCy/Koreferenz-Analyse: " + str(e))
        return []

    try:
        initial_words = find_initial_words(doc)
    except Exception as e:
        loguru.logger.error("Fehler bei der Initialerkennung maskuliner Formen: " + str(e))
        return []

    for word in initial_words:
        print(word.idx)
        try:
            needs_gendering, reason = needs_to_be_gendered(doc, word)
        except Exception as e:
            loguru.logger.error(f"Fehler bei needs_to_be_gendered() für '{word.text}': {e}")
            result.append({
                "word": word.text,
                "from": word.idx,
                "to": word.idx + len(word.text),
                "possibleCorrections": [],
                "shouldBeGendered": False,
                "reasonNotGendered": [("", f"Fehler: {str(e)}")],
                "errors": [str(e)]
            })
            continue

        if not needs_gendering:
            result.append({
                "word": word.text,
                "from": word.idx,
                "to": word.idx + len(word.text),
                "possibleCorrections": [],
                "shouldBeGendered": False,
                "reasonNotGendered": reason,
                "errors": []
            })
            continue

        try:
            context_words = get_coref_words_in_sentence(doc, word)
            possible_corrections, errors = generate_possible_corrections(context_words)
            result.append({
                "word": word.text,
                "from": word.idx,
                "to": word.idx + len(word.text),
                "possibleCorrections": possible_corrections,
                "shouldBeGendered": True,
                "reasonNotGendered": [],
                "errors": errors
            })
        except Exception as e:
            loguru.logger.exception(f"Fehler bei generate_possible_corrections() für '{word.text}': {e}")
            result.append({
                "word": word.text,
                "from": word.idx,
                "to": word.idx + len(word.text),
                "possibleCorrections": [],
                "shouldBeGendered": True,
                "reasonNotGendered": [],
                "errors": [str(e)]
            })

    return sorted(result, key=lambda x: x["from"])
