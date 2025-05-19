def find_in_result(rlist, _from, _to):
    return next((w for w in rlist if w["from"] == _from and w["to"] == _to), None)

def update_counts(counter ,ntbg, was_correct, is_noun, is_singular, was_marked):
    if(was_marked):
        counter["marks"] += 1
    else:
        counter["not_marked"] += 1
    counter["correct" if was_correct else "incorrect"] += 1

    label = "ntbg" if ntbg else "not_ntbg"
    counter[label] += 1
    counter[f"{label}_{'correct' if was_correct else 'incorrect'}"] += 1

    typ = "nouns" if is_noun else "pronouns"
    counter[typ] += 1
    counter[f"{typ}_{label}"] += 1
    counter[f"{typ}_{label}_{'correct' if was_correct else 'incorrect'}"] += 1

    if is_singular == None:
        counter["num_undetermined"] += 1
    else:
        sgpl = "singular" if is_singular else "plural"
        counter[sgpl] += 1
        counter[f"{label}_{sgpl}"] += 1
        counter[f"{sgpl}_{label}_{'correct' if was_correct else 'incorrect'}"] += 1


from collections import defaultdict
# Diese funktion soll dazu dienen durch die Markierten Wörter zu iterieren und festzustellen ob sie im pipeline Ergebniss vorhanden sind
def compare_marked_to_pipeline(global_counts,marked, pipeline_result, spacify):
    local_counts = defaultdict(int)
    seen_positions = set()
    for entry in marked: 
        word_in_pipeline_result = find_in_result(pipeline_result, entry['from'], entry['to'])
        begin_ = [x for x in spacify if x.idx == entry["from"]]
        if not begin_:
            print(f"could not find: {entry}")
            continue
        _word = begin_[0]
        seen_positions.add((entry['from'], entry['to']))
        #muss es gegendert werden
        needs_to_be_gendered = entry['ntbg']

        #lag die pipeline richtig
        if word_in_pipeline_result: 
            was_correct = word_in_pipeline_result['shouldBeGendered'] == needs_to_be_gendered
        else:
            was_correct = not needs_to_be_gendered

        #ist es ein nomen 
        is_noun = _word.pos_ == 'NOUN'

        #Singular, plural oder undefined
        if _word.morph.get("Number") and _word.morph.get("Number")[0]:
            number = _word.morph.get("Number")[0]
            is_singular = number == "Sing"
        else:
            is_singular = None
 
        update_counts(local_counts, needs_to_be_gendered, was_correct, is_noun, is_singular, True)
        update_counts(global_counts, needs_to_be_gendered, was_correct, is_noun, is_singular, True)
            # 2. Suche nach False Positives – also Wörter, die im Pipeline-Ergebnis auftauchen,
    # aber nicht im Markup
    for entry in pipeline_result:
        pos = (entry['from'], entry['to'])
        if pos in seen_positions:
            continue  # wurde oben bereits verarbeitet

        if not entry['shouldBeGendered']:
            continue  # das System hat korrekt nichts markiert

        begin_ = [x for x in spacify if x.idx == entry["from"]]
        if not begin_:
            print(f"could not find in spacify: {entry}")
            continue
        _word = begin_[0]

        is_noun = _word.pos_ == 'NOUN'
        number = _word.morph.get("Number")
        is_singular = number[0] == "Sing" if number else None

        # False Positive: das System hat etwas gegendert, das nicht hätte gegendert werden sollen
        update_counts(local_counts, False, False, is_noun, is_singular, False)
        update_counts(global_counts, False, False, is_noun, is_singular,False)

    return local_counts
            