#!/usr/bin/env python3

import argparse
from pymystem3 import Mystem


def bpe_processing(filenames: list[str]):
    pass


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

