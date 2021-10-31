#!/usr/bin/env python3

import argparse


def dfs(ru_to_zh, zh_to_ru, from_, is_ru=True):
    black_ru = set()
    black_zh = set()
    gray_ru = set()
    gray_zh = set()

    stack = [(from_, is_ru)]

    while stack:
        cur, is_ru = stack.pop(-1)
        if is_ru:
            black_ru.add(cur)
            iterate = ru_to_zh
            gray = gray_zh
            black = black_zh
        else:
            black_zh.add(cur)
            iterate = zh_to_ru
            gray = gray_ru
            black = black_ru
        for new in iterate[cur]:
            if new not in gray and new not in black:
                stack.append((new, not is_ru))
    return black_ru, black_zh


def join_alignment(line):
    pairs = [tuple(map(int, pair.split("-"))) for pair in line.split()]
    ru_to_zh = {}
    zh_to_ru = {}
    all_ru = set()
    for ru, zh in pairs:
        ru_to_zh[ru] = ru_to_zh.get(ru, set()) | {zh}
        zh_to_ru[zh] = zh_to_ru.get(zh, set()) | {ru}
        all_ru.add(ru)
    black_ru = set()
    components = []
    for ru in all_ru:
        if ru not in black_ru:
            ru_set, zh_set = dfs(ru_to_zh, zh_to_ru, ru)
            black_ru.update(ru_set)
            components.append((ru_set, zh_set))
    return components


parser = argparse.ArgumentParser(description="Get offset pairs from alignment pairs")
parser.add_argument("alignment", type=str, help="alignment file")
parser.add_argument("offsets", type=str, help="offsets file")

parser_args = parser.parse_args()
alignment_filename = parser_args.alignment
offsets_filename = parser_args.offsets

with open(alignment_filename, "r") as alignment_file, open(offsets_filename, "r") as offsets_file:
    for alignment_line, offsets_line in zip(alignment_file, offsets_file):
        filename, ru_hash, zh_hash, ru_offsets, zh_offsets = offsets_line.split(" ||| ")
        components = join_alignment(alignment_line)
        ru_offsets = ru_offsets.split()
        zh_offsets = zh_offsets.split()
        offset_alignment = []
        for component_ru, component_zh in components:
            ru_off = [ru_offsets[i] for i in component_ru]
            zh_off = [zh_offsets[i] for i in component_zh]
            offset_alignment.append(f"{','.join(ru_off)}:{','.join(zh_off)}")
        print(f"{filename} ||| {ru_hash} ||| {zh_hash} ||| {'|'.join(offset_alignment)}")