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