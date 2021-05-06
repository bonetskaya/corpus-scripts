#!/usr/bin/env python3

import argparse
from pymystem3 import Mystem
from io import StringIO
from subword_nmt.learn_bpe import learn_bpe
from subword_nmt.apply_bpe import BPE


def ru_tokenize(sentence):
    return sentence.split()


def zh_tokenize(sentence):
    return [sentence]


def token_map(tokens: list[str]) -> list[str]:
    result = []
    word_num = 1
    for token in tokens:
        result.append(str(word_num))
        if not token.endswith("@@"):
            word_num += 1

    return result


def bpe_processing(filenames: list[str]):
    ru_sentences = []
    zh_sentences = []

    for filename in filenames:
        with open(filename, "r") as f:
            for line in f:
                ru, zh = line.split(" ||| ")
                ru_sentences.append(ru)
                zh_sentences.append("".join(zh.split(" ")))

    bpe = {}
    learn_bpe(StringIO("\n".join(ru_sentences)), open('bpe_rules.ru', 'w'), num_symbols=8000)
    bpe["ru"] = BPE(open('./bpe_rules.ru'))
    learn_bpe(StringIO("\n".join(zh_sentences)), open('bpe_rules.zh', 'w'), num_symbols=8000)
    bpe["zh"] = BPE(open('./bpe_rules.zh'))

    with open("token_map.txt", "w") as f:
        for ru, zh in zip(ru_sentences, zh_sentences):
            ru_tokens = bpe["ru"].process_line(ru)
            zh_tokens = bpe["zh"].process_line(zh)
            ru_map = token_map(ru_tokens)
            zh_map = token_map(zh_tokens)
            print(" ".join(ru_map) + " + " + " ".join(zh_map), file=f)
            print(ru_tokens + " ||| " + zh_tokens)


def lemmatize(filenames: list[str]):
    mystem = Mystem()
    for filename in filenames:
        with open(filename, "r") as f:
            for line in f:
                ru, zh = line.split("|||")
                ru_lem = mystem.lemmatize(ru)
                zh_lem = mystem.lemmatize(zh)
                print("".join(ru_lem)[:-1] + "|||" + "".join(zh_lem)[:-1])


parser = argparse.ArgumentParser(description="Preprocess sentences (bpe-tokenization or lemmatisation)")
parser.add_argument("filenames", nargs="+", type=str, help="pharaoh filenames")
parser.add_argument("-t", "--type", nargs=1, type=str, help="preprocess type (bpe, lemma)")

parser_args = parser.parse_args()
filenames = parser_args.filenames
preprocess_type = parser_args.type[0]

preprocess_types = ("bpe", "lemma")

if preprocess_type not in preprocess_types:
    raise Exception(f"{preprocess_type} is wrong type, choose from {', '.join(preprocess_types)}.")

if preprocess_type == "bpe":
    bpe_processing(filenames)
elif preprocess_type == "lemma":
    lemmatize(filenames)

