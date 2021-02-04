#!/usr/bin/env python3

import argparse
import csv

from nltk.tokenize import WordPunctTokenizer
from pymystem3 import Mystem


parser = argparse.ArgumentParser(description="Get pharaoh alignment from tsv file."
                                             "Also create pairs.txt with tokenized pairs of sentences.")
parser.add_argument("tsv", nargs="+", type=str, help="tsv with alignment")

parser_args = parser.parse_args()
filename = parser_args.tsv[0]

mystem_analyzer = Mystem()
aligned_sentences = []
ru_lem_sentences = []

tokenized_pairs = []

with open(filename, "r") as csvfile:
    for i, line in enumerate(csv.reader(csvfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_MINIMAL)):
        if i % 5 == 0:
            ru_lem = list(filter(lambda x : not x[0].isspace(),
                                 mystem_analyzer.lemmatize(line[0])))
            ru_lem_sentences.append(ru_lem)
            ru_tokenized = WordPunctTokenizer().tokenize(line[0])
            if len(ru_tokenized) != len(ru_lem):
                ru_tokenized = ru_lem
        if i % 5 == 2:
            zh_align = list(filter(lambda x: len(x) > 0, line))

            tokenized_pair = " ".join(ru_tokenized) + " ||| " + " ".join(zh_align)
            tokenized_pairs.append(tokenized_pair)
        if i % 5 == 3:
            ru_align = line[:len(zh_align)]
            aligned_sentences.append((zh_align, ru_align))


with open("pharaoh.txt", "w") as ph:
	for aligned_sentence, ru_lem_sentence in zip(aligned_sentences, ru_lem_sentences):
		zh_sent, ru_sent = aligned_sentence
		for i, (zh, ru) in enumerate(zip(zh_sent, ru_sent)):
			if len(zh) == 0 or len(ru) == 0 or ru not in ru_lem_sentence:
				continue
			# print(f"{ru_lem_sentence.index(ru) + 1}-{i + 1}", end=" ")
			print(f"{ru_lem_sentence.index(ru) + 1}-{i + 1}", end=" ", sep="\n", file=ph)
		print()

with open("pairs.txt", "w") as f:
    print(*tokenized_pairs, sep="\n", file=f)
