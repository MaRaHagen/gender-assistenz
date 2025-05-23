# Gibt die Kinder zurück, die mit einer bestimmten
# Relationseigenschaft (app, ...) verbunden sind.
def follow_child_dep(word, rel):
    if type(rel) is not list:
        rel = [rel]

    result = []
    for child in word.children:
        if child.dep_ in rel:
            result.append(child)

    return result


# Gibt maximal ein Kind zurück, welches mit einer bestimmten
# Relationseigenschaft (app, ...) verbunden sind.
def follow_child_dep_single_or_none(word, rel):
    result = follow_child_dep(word, rel)

    if len(result) > 1:
        raise Exception(f"Es darf nur ein Element mit dieser Beziehung geben. ({word} mit {rel}, war aber {result})")

    if not result:
        return None

    return result[0]

# Gibt das Elternteil zurück, wenn dieses mit einer bestimmten
# Relationseigenschaft (app, ...) verbunden ist, ansonsten None.
def follow_parent_dep(word, rel):
    if type(rel) is not list:
        rel = [rel]

    if word.dep_ in rel:
        return word.head

    return None

"""
Geht rekursiv nach oben im Baum, solange die aktuelle Dependenz in 'rels' ist.
Vermeidet endlose Schleifen durch Begrenzung von max_depth.
"""
def follow_parent_dep_recursive(word, rels, max_depth=10):

    if isinstance(rels, str):
        rels = [rels]

    current = word
    depth = 0

    while depth <= max_depth:
        if current.dep_ in rels and current.head != current:
            return current.head
        else:
            current = current.head
            depth += 1
    return None

def get_coref_words_in_sentence(doc, word):
    result = []

    #
    # Alle Coref-Chains durchgehen:
    #
    for chain in doc._.coref_chains:
        mention_indices = [x.root_index for x in chain]

        if word.i in mention_indices:
            for owi in mention_indices:
                # Es intressieren uns nur Wörter, die im gleichen Satz stehen.
                if word.doc[owi].sent != word.sent:
                    continue

                result.append(word.doc[owi])

    if not result:
        result = [word]

    return result
