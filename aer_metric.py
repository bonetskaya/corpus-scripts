#!/usr/bin/env python3

import argparse


def get_pairs(filename: str) -> list[list[(int, int)]]:
    pairs = []
    with open(filename, "r") as f:
        for line in f:
            str_pairs = line.split()
            if len(str_pairs) == 0:
                continue
            pairs.append([])
            for pair in str_pairs:
                fi, se = pair.split("-")
                pairs[-1].append((int(fi), int(se)))
    return pairs


def compute_precision(reference: list[list[(int, int)]], predicted: list[list[(int, int)]]) -> (int, int):
    numerator = 0
    denominator = 0
    for i in range(len(predicted)):
        for pair in reference[i]:
            if pair in predicted[i]:
                numerator += 1
        denominator += len(predicted[i])
    return numerator, denominator


def compute_recall(reference: list[list[(int, int)]], predicted: list[list[(int, int)]]) -> (int, int):
    numerator = 0
    denominator = 0
    for i in range(len(predicted)):
        for pair in reference[i]:
            if pair in predicted[i]:
                numerator += 1
        denominator += len(reference[i])
    return numerator, denominator


def compute_aer(reference: list[list[(int, int)]], predicted: list[list[(int, int)]]) -> float:
    precision = compute_precision(reference, predicted)
    recall = compute_recall(reference, predicted)
    return 1 - (precision[0] + recall[0]) / (precision[1] + recall[1])


parser = argparse.ArgumentParser(description="Count AER for two alignments.")
parser.add_argument("-r", "--reference_alignment", nargs=1, type=str, help="filename for pharaoh reference alignment")
parser.add_argument("-p", "--predicted_alignment", nargs=1, type=str, help="filename for pharaoh predicted alignment")

parser_args = parser.parse_args()
filename_prediction = parser_args.predicted_alignment[0]
filename_reference = parser_args.reference_alignment[0]

prediction = get_pairs(filename_prediction)
reference = get_pairs(filename_reference)

print(compute_aer(reference, prediction))
