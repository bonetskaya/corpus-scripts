#!/usr/bin/env python3

import argparse
import json
from nltk.tokenize import word_tokenize


parser = argparse.ArgumentParser(description="Get tokenized sentences from json. Output example:\n русский ||| 中文")
parser.add_argument("filenames", nargs="+", type=str, help="json filenames")
parser.add_argument("-t", "--tokenizer", nargs=1, type=str, help="tokenization type (nltk)", default=["nltk"])

parser_args = parser.parse_args()
filenames = parser_args.filenames
tokenization = parser_args.tokenizer[0]


all_sentences = {}

for filename in filenames:
    with open(filename) as json_file:
        data_json = json.load(json_file)
        for sentence_json in data_json["sentences"]:
            sentence = sentence_json["text"]
            id = sentence_json["para_alignment"][0]["para_id"]
            lang = sentence_json["lang"]
            all_sentences[id] = all_sentences.get(id, []) + [(lang, sentence)]

    result = []
    for sentence_pair in all_sentences.values():
        if len(sentence_pair) != 2:
            continue
        if len(sentence_pair[0][1]) == 0 or len(sentence_pair[1][1]) == 0:
            continue
        if sentence_pair[0][0] != 0:
            sentence_pair = (sentence_pair[1], sentence_pair[0])

        rus = word_tokenize(sentence_pair[0][1])
        zh = word_tokenize(sentence_pair[1][1])
        print(" ".join(rus) + " ||| " + " ".join(zh))

