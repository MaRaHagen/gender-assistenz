import json
import re
import dataset
from lxml import etree as ET

from utils.regex import regex_first_or_none, regex_nth_or_none

db = dataset.connect('sqlite:///words.db')

words_table = db['words']


# def read_file(path):
#     file = open(path, mode='r', encoding="utf-8")
#     contents = file.read()
#     file.close()
#
#     return contents

continue_print = False

def print_cnt(str):
    if continue_print:
        print(str)

result = []

# Namespace der Tags innerhalb des Wiktionary-Exports
ns = "{http://www.mediawiki.org/xml/export-0.11/}"

for event, page_tag in ET.iterparse("dewiktionary-20250520-pages-articles.xml", events=("end",), tag=f"{ns}page"):
    title = page_tag.find(f"{ns}title")

    #if title.text == "Kickerin":
    #    continue

    revision_tag = page_tag.find(f"{ns}revision")

    # is None, statt not, da ein Tag bei lxml eine Liste ist und eine leere Liste als falsy ausgewertet wird.
    if revision_tag is None:
        print_cnt("no revision tag for page, skipping...")
        continue

    text_tag = revision_tag.find(f"{ns}text")

    if text_tag is None:
        print_cnt("no text tag in revision tag for page, skipping...")
        continue

    text = text_tag.text

    if not text or ("Deutsch Substantiv" not in text and "Substantiv|Deutsch" not in text):
        print_cnt(f"{title.text} ist kein Substantiv")
        continue

    multiple_meaning_texts = text.split("\n=== {{Wortart|Substantiv|Deutsch}}")[1:]


    for text in multiple_meaning_texts:
        if len(multiple_meaning_texts) > 2:
            print(f"{title.text} has multiple meanings: {len(multiple_meaning_texts) - 1}")

        # Genus auslesen
        genus = regex_first_or_none('\\|Genus=([a-z])', text)
        if not genus:
            genus = regex_first_or_none('\\|Genus 1=([a-z])', text)
            if not genus:
                print_cnt(f"{title.text} enthält keine Genus-Informationen")
                continue

        formen = [
            "Nominativ Singular",
            "Nominativ Plural",
            "Genitiv Singular",
            "Genitiv Plural",
            "Dativ Singular",
            "Dativ Plural",
            "Akkusativ Singular",
            "Akkusativ Plural",

            "Nominativ Plural 1",
            "Genitiv Plural 1",
            "Dativ Plural 1",
            "Akkusativ Plural 1",

            "Nominativ Plural 2",
            "Genitiv Plural 2",
            "Dativ Plural 2",
            "Akkusativ Plural 2",

            "Nominativ Singular 1",
            "Genitiv Singular 1",
            "Dativ Singular 1",
            "Akkusativ Singular 1"
        ]
        formen_result = []

        stamm = regex_first_or_none(f"\\|Stamm=(.*)\n", text)

        if not "Deutsch adjektivisch" in text or not stamm:
            for form in formen:
                form_result = regex_first_or_none(f"\\|{form}=(.*)\n", text)

                formen_result.append(form_result.strip() if form_result is not None else None)
        else:
            formen_result.append(stamm + "r")
            formen_result.append(stamm + "")
            formen_result.append(stamm + "n")
            formen_result.append(stamm + "r")
            formen_result.append(stamm + "m")
            formen_result.append(stamm + "n")
            formen_result.append(stamm + "n")
            formen_result.append(stamm + "")

            formen_result.append("")
            formen_result.append("")
            formen_result.append("")
            formen_result.append("")

            formen_result.append("")
            formen_result.append("")
            formen_result.append("")
            formen_result.append("")

            formen_result.append("")
            formen_result.append("")
            formen_result.append("")
            formen_result.append("")

        #print(formen_result)

        # Bsp.: [[Portierfrau]], [[Portierin]], [[Portiersfrau]]
        weibliche_formen_raw = regex_nth_or_none("Weibliche Wortformen}}\\n:\\[(.*)?\\] (.*)", text, 1)
        if not weibliche_formen_raw:
            w = regex_nth_or_none("Weibliche Wortformen}}\\n:\\[\\[(.*)?\\]\\]", text, 0)
            if w:
                weibliche_formen_raw = "[[" + w + "]]"

        weibliche_formen_matches = None
        if weibliche_formen_raw:
            weibliche_formen_matches = re.findall("\\[\\[(.*)?\\]\\]", weibliche_formen_raw)

        maennliche_formen_raw = regex_nth_or_none("Männliche Wortformen}}\\n:\\[(.*)?\\] (.*)", text, 1)
        if not maennliche_formen_raw:
            m = regex_nth_or_none("Männliche Wortformen}}\\n:\\[\\[(.*)?\\]\\]", text, 0)
            if m:
                maennliche_formen_raw = "[[" + m + "]]"

        maennliche_formen_matches = None
        if maennliche_formen_raw:
            maennliche_formen_matches = re.findall("\\[\\[(.*)?\\]\\]", maennliche_formen_raw)

        if not maennliche_formen_matches and not weibliche_formen_matches:
            print_cnt(f"{title.text} enthält weder männliche noch weibliche Formen.")
            continue

        print(title.text + f" [{genus}]")
        result += title.text + f" [{genus}]"

        words_table.insert(
            dict(
                title=title.text,
                genus=genus,

                nominativ_singular=formen_result[0] if formen_result[0] else formen_result[16],
                nominativ_plural=formen_result[1] if formen_result[1] else formen_result[8],
                genitiv_singular=formen_result[2] if formen_result[2] else formen_result[17],
                genitiv_plural=formen_result[3] if formen_result[3] else formen_result[9],
                dativ_singular=formen_result[4] if formen_result[4] else formen_result[18],
                dativ_plural=formen_result[5] if formen_result[5] else formen_result[10],
                akkusativ_singular=formen_result[6] if formen_result[6] else formen_result[19],
                akkusativ_plural=formen_result[7] if formen_result[7] else formen_result[11],

                nominativ_plural1=formen_result[8],
                genitiv_plural1=formen_result[9],
                dativ_plural1=formen_result[10],
                akkusativ_plural1=formen_result[11],
                nominativ_plural2=formen_result[12],
                genitiv_plural2=formen_result[13],
                dativ_plural2=formen_result[14],
                akkusativ_plural2=formen_result[15],

                maennliche_formen=None if not maennliche_formen_matches else json.dumps(maennliche_formen_matches),
                weibliche_formen=None if not weibliche_formen_matches else json.dumps(weibliche_formen_matches)
            )
        )

    page_tag.clear()

print(len(result))

db.close()