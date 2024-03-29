#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

# make-dict2.py で変換したものを再変換.
#
import json
from pathlib import Path
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dict', type=Path, help='file path(s) to parse', default=Path("dict/correction.json"))
parser.add_argument('--out', type=Path, help='file path(s) to parse', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')

with (Path(__file__).parent if '__file__' in locals() else Path().cwd().joinpath('tools')).joinpath('params.json').open('r') as fp:
    params = json.load(fp)
    print("""Valheim version: {LATEST_VERSION}\r\nTarget Language: {LANG}""".format(**params))
    if( "out" not in vars(args)):
        args.out = Path(f"dict/CorrectText_{params['LANG']}.json")
    else:
        if(args.out is None):
            args.out = Path(f"output/CorrectText_{params['LANG']}.json")

with args.dict.open("r", encoding="utf-8") as f:
    dict_with_metadata = json.load(f)
    print(f"json file is loaded from {args.dict}")

dict1 = {k:v[params["LANG"]]["text"] for l in dict_with_metadata.values() for (k, v) in l.items()}

with args.out.open("w", encoding="utf-8") as f:
    json.dump(dict1, f, ensure_ascii=False, indent=2)
    print(f"json file is exported at {args.out}")
unity_path = Path("Unity/Assets/Text")
if not unity_path.exists:
    unity_path.mkdir(exist_ok=True)
with unity_path.joinpath(args.out.name) as fp:
    with fp.open("w", encoding="utf-8") as f:
        json.dump(dict1, f, ensure_ascii=False, indent=2)
    print(f"json file is exported at {fp}")