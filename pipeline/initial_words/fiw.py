from loguru import logger


def find_initial_words(doc):
    """
    Findet alle potenziellen generisch-maskulinen Formen im Dokument,
    darunter maskuline Nomen und relevante maskuline Pronomen (3. Person, Singular),
    wobei problematische Stopwörter ausgeschlossen werden.
    """
    result = []
    stop_words = {
        "niemand", "jemand", "man", "wer", "was", "selbst", "selber",
        "derlei", "dergleichen", "einander", "beide", "viele", "irgendwem", "irgendjemand"
    }

    for word in doc:
        gender = word.morph.get("Gender")
        person = word.morph.get("Person")
        number = word.morph.get("Number")
        is_stop_word = any(word.text.lower().startswith(x) for x in stop_words)

        # Maskuline Nomen
        if word.pos_ == "NOUN" and gender and gender[0] == "Masc":
            result.append(word)

        # Maskuline Pronomen (nur 3. Person, Singular, kein Stopwort)
        elif (
                word.pos_ == "PRON" and
                gender and gender[0] == "Masc" and
                word.tag_ in {"PDS", "PIS", "PPER", "PPOSS", "PRELS"} and
                (not person or person[0] == "3") and
                (not number or number[0] == "Sing") and
                not is_stop_word
        ):
            result.append(word)

    return result
    #
    # logger.debug(f"Result before filtering: {result}")
    #
    # words_to_remove = []
    # for r in result:
    #     # Fall: Ist das Pronomen Subjekt eines Relativsatzes, der sich auf
    #     #       ein bereits gefundenes Wort bezieht?
    #     #
    #     #       Wenn ja, entfernen wir das Wort, da wir das Pronomen im Rahmen
    #     #       des anderen Worts betrachten.
    #     #
    #     #       Bsp.: Derjenige, der sich impfen lassen will, der sollte einen Krankheitstag wegen Impfnebenwirkungen einplanen.
    #     #             _________  ___
    #     #
    #     subject_parent = follow_parent_dep(r[0], "sb")
    #     if subject_parent:
    #         relative_clause_parent = follow_parent_dep(subject_parent, "rc")
    #
    #         if relative_clause_parent and relative_clause_parent in [x[0] for x in result]:
    #             words_to_remove.append(r)
    #             logger.debug(f"Remove: {r[0].text} (relative clause rule)")
    #
    #     # Fall: Ist das Pronomen ein wiederholendes Pronomen bezüglich eines anderen
    #     #       bereits ermittelten Pronomen?
    #     #
    #     #       Bsp.: Derjenige, der sich impfen lassen will, der sollte einen Krankheitstag wegen Impfnebenwirkungen einplanen.
    #     #             _________                               ___
    #     #
    #     repeated_parent = follow_parent_dep(r[0], "re")
    #     if repeated_parent and repeated_parent in [x[0] for x in result]:
    #         words_to_remove.append(r)
    #         logger.debug(f"Remove: {r[0].text} (repeated element rule)")
    #
    #     # Fall: Beschreibt das Pronomen ein verwendetes Nomen oder ein anderes Pronomen, dann markieren wir nur
    #     #       das Nomen.
    #     #
    #     #       Bsp.: Bundeswirtschaftsminister Werner Müller, derjenige, der davon profitiert, freut sich über solche Aussichten.
    #     #             _________________________                _________
    #     app_parent = follow_parent_dep(r[0], "app")
    #     if app_parent and app_parent in [x[0] for x in result]:
    #         words_to_remove.append(r)
    #         logger.debug(f"Remove: {r[0].text} (apposition rule)")
    #
    # return [x for x in result if x not in words_to_remove]