#!/usr/bin/env python3

import argparse
import hashlib
import json
import os


class Sentence:
    def __init__(self, text, lang, offsets, text_hash):
        assert len(text.split()) == len(offsets.split())
        self.text = text
        self.lang = lang
        self.offsets = offsets
        self.text_hash = text_hash


def get_text_offset(sentence_json):
    words = []
    offsets = []
    for word in sentence_json["words"]:
        if len(word["wf"]) == 0:
            return "", ""
        if len(word["wf"].split()) == 1:
            words.append(word["wf"])
            offsets.append(f"{word['off_start']}-{word['off_end']}")
        else:
            off_start = word['off_start']
            current_start_idx = 0
            current_end_idx = len(word["wf"])
            while word["wf"][current_start_idx].isspace():
                current_start_idx += 1
            while word["wf"][current_end_idx - 1].isspace():
                current_end_idx -= 1
            assert len(word["wf"].strip()) == current_end_idx - current_start_idx
            for i, sym in enumerate(word["wf"].strip()):
                if sym.isspace():
                    words.append(word["wf"][current_start_idx: i])
                    offsets.append(f"{off_start + current_start_idx}-{off_start + i}")
                    current_start_idx = i
            words.append(word["wf"][current_start_idx: current_end_idx])
            offsets.append(f"{off_start + current_start_idx}-{off_start + current_end_idx}")
    return " ".join(words), " ".join(offsets)


parser = argparse.ArgumentParser(description="Get tokenized sentences from json. Output example:\n русский ||| 中文")
parser.add_argument("filenames", nargs="+", type=str, help="json filenames")

parser_args = parser.parse_args()
filenames = parser_args.filenames


all_sentences = {}
cnt = 0
info_for_alignment = []
for filename in filenames:
    with open(filename, "r") as json_file:
        data_json = json.load(json_file)
        for sentence_json in data_json["sentences"]:
            sentence, offsets = get_text_offset(sentence_json)
            idx = sentence_json["para_alignment"][0]["para_id"]
            lang = sentence_json["lang"]
            sentence_json["hash"] = hashlib.sha1(sentence_json["text"].encode("utf-8")).hexdigest()
            all_sentences[idx] = all_sentences.get(idx, []) + [Sentence(sentence, lang, offsets, sentence_json["hash"])]
    os.remove(filename)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False)

    result = []
    for _, sentence_pair in all_sentences.items():
        if len(sentence_pair) != 2:
            continue
        if len(sentence_pair[0].text) == 0 or len(sentence_pair[1].text) == 0:
            continue
        if sentence_pair[0].lang != 0:
            sentence_pair = (sentence_pair[1], sentence_pair[0])
        print(sentence_pair[0].text + " ||| " + sentence_pair[1].text)
        info_for_alignment.append(f"{filename} ||| {sentence_pair[0].text_hash} ||| {sentence_pair[1].text_hash} ||| {sentence_pair[0].offsets} ||| {sentence_pair[1].offsets}")
with open("sentences_info", "w") as f:
    print("\n".join(info_for_alignment), file=f)
