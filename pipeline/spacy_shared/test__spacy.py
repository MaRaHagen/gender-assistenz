from _spacy import spacify_with_coref


def test_spacify_with_coref():
    doc = spacify_with_coref("Er geht sein Eis essen.")

    doc._.coref_chains.print()

def test_spacify_with_coref_mulitple_sentences_coref_is_first():
    doc = spacify_with_coref("Yitzhak Rabin war Ministerpräsident. Er strebte nach Frieden.")

    doc._.coref_chains.print()

def test_spacify_with_coref_mulitple_sentences_coref_second():
    doc = spacify_with_coref("""Der Saarländer aber gewann die Herzen der Genossen
                             In einem spannenden Duell entriß Oskar Lafontaine dem Amtsinhaber Rudolf Scharping den SPD-Vorsitz""")
    doc._.coref_chains.print()