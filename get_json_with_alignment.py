#!/usr/bin/env python3

import argparse
import json
import os


def get_offsets(offsets, cur_max_id):
    clusters = offsets.split("|")
    ru = []
    zh = []
    for cluster in clusters:
        ru_p, zh_p = cluster.split(":")
        ru += [{"off_start": int(x.split("-")[0]), "off_end": int(x.split("-")[1]), "para_id": cur_max_id} for x in ru_p.split(",")]
        zh += [{"off_start": int(x.split("-")[0]), "off_end": int(x.split("-")[1]), "para_id": cur_max_id} for x in zh_p.split(",")]
        cur_max_id += 1
    return ru, zh, cur_max_id

max_id = 1000000000000


parser = argparse.ArgumentParser(description="Add alignment to json")
parser.add_argument("offset_alignment", type=str, help="alignment file")
parser.add_argument("jsons", nargs="+", type=str, help="offsets file")

parser_args = parser.parse_args()
offset_alignment_filename = parser_args.offset_alignment
jsons = parser_args.jsons

current_json_filename = ""
ru_hash_to_zh_offsets = {}

with open(offset_alignment_filename, "r") as alignment_file:
    for line in alignment_file:
        json_filename, ru_hash, zh_hash, alignment = line.split(" ||| ")
        if json_filename != current_json_filename:
            if current_json_filename:
                os.remove(current_json_filename)
                with open(current_json_filename, "w", encoding="utf-8") as f:
                    json.dump(data_json, f, ensure_ascii=False)
            current_json_filename = json_filename
            with open(json_filename, "r") as json_file:
                data_json = json.load(json_file)
            i = 0
        while i < len(data_json["sentences"]) and data_json["sentences"][i]["hash"] != ru_hash:
            i += 1
        if i >= len(data_json["sentences"]):
            print("assert")
            break
        # data_json["sentences"][i]["para_alignment"][0]["off_end"] = data_json["sentences"][i]["para_alignment"][0]["off_start"]
        ru, zh, max_id = get_offsets(alignment, max_id)
        data_json["sentences"][i]["para_alignment"] = ru
        ru_hash_to_zh_offsets[ru_hash] = zh

os.remove(current_json_filename)
with open(current_json_filename, "w", encoding="utf-8") as f:
    json.dump(data_json, f, ensure_ascii=False)

current_json_filename = ""
with open(offset_alignment_filename, "r") as alignment_file:
    for line in alignment_file:
        json_filename, ru_hash, zh_hash, alignment = line.split(" ||| ")
        if json_filename != current_json_filename:
            if current_json_filename:
                os.remove(current_json_filename)
                with open(current_json_filename, "w", encoding="utf-8") as f:
                    json.dump(data_json, f, ensure_ascii=False)
            current_json_filename = json_filename
            with open(json_filename, "r") as json_file:
                data_json = json.load(json_file)
            i = 0
        while i < len(data_json["sentences"]) and data_json["sentences"][i]["hash"] != zh_hash:
            i += 1
        if i >= len(data_json["sentences"]):
            print("assert")
            break
        # data_json["sentences"][i]["para_alignment"][0]["off_end"] = data_json["sentences"][i]["para_alignment"][0]["off_start"]
        zh = ru_hash_to_zh_offsets[ru_hash]
        data_json["sentences"][i]["para_alignment"] = zh

os.remove(current_json_filename)
with open(current_json_filename, "w", encoding="utf-8") as f:
    json.dump(data_json, f, ensure_ascii=False)
