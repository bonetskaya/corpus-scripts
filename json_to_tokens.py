#!/usr/bin/env python3

import argparse
import json


class Sentence:
    text: str
    lang: int

    def __init__(self, text, lang):
        self.text = text
        self.lang = lang


parser = argparse.ArgumentParser(description="Get tokenized sentences from json. Output example:\n русский ||| 中文")
parser.add_argument("filenames", nargs="+", type=str, help="json filenames")

parser_args = parser.parse_args()
filenames = parser_args.filenames


all_sentences = {}

for filename in filenames:
    with open(filename) as json_file:
        data_json = json.load(json_file)
        for sentence_json in data_json["sentences"]:
            sentence = " ".join([word["wf"] for word in sentence_json["words"]]).replace("\n", "")
            id = sentence_json["para_alignment"][0]["para_id"]
            lang = sentence_json["lang"]
            all_sentences[id] = all_sentences.get(id, []) + [Sentence(sentence, lang)]

    result = []
    for sentence_pair in all_sentences.values():
        if len(sentence_pair) != 2:
            continue
        if len(sentence_pair[0].text) == 0 or len(sentence_pair[1].text) == 0:
            continue
        if sentence_pair[0].lang != 0:
            sentence_pair = (sentence_pair[1], sentence_pair[0])
        print(sentence_pair[0].text + " ||| " + sentence_pair[1].text)
