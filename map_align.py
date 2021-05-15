#!/usr/bin/env python3

import argparse


parser = argparse.ArgumentParser(description="Gets alignment after transformation using transformation map")
parser.add_argument("-a", "--alignment", nargs=1, type=str, help="pharaoh alignment file")
parser.add_argument("-m", "--map", nargs=1, type=str, help="transformation file")

parser_args = parser.parse_args()
alignment_filename = parser_args.alignment[0]
map_filename = parser_args.map[0]

with open(alignment_filename, "r") as alignment_file, open(map_filename, "r") as map_file:
    for align_line, map_line in zip(alignment_file, map_file):
        ru_map, zh_map = map_line.split("|||")
        ru_dict = {int(pair.split(", ")[0]) - 1: int(pair.split(", ")[1]) - 1 for pair in ru_map.strip()[1:-1].split(") (")}
        zh_dict = {}
        for pair in zh_map.strip()[1:-1].split(") ("):
            k, v = pair.split(", ")
            k, v = int(k) - 1, int(v) - 1
            zh_dict[k] = zh_dict.get(k, []) + [v]
        prev_alignment = [tuple(pair.split("-")) for pair in align_line.split()]

        new_alignment = set()
        for p1, p2 in prev_alignment:
            pair = int(p1), int(p2)
            new_ru = ru_dict[pair[0]]
            new_zh = zh_dict[pair[1]]
            for zh_token in new_zh:
                new_alignment.add((new_ru, zh_token))

        for pair in new_alignment:
            print(f"{pair[0]}-{pair[1]}", end=" ")
        print()
