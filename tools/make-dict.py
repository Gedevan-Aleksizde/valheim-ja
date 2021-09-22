#! /usr/bin/env python 
import json
from pathlib import Path
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--filename', type=Path, help='file path(s) to parse', default=None)
parser.add_argument('--output', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')

input = Path('l10n.xlsx') if args.filename is None else args.filename
output = Path().cwd().joinpath('dict/correction.json') if args.output is None else args.output
if not output.parent.exists():
    output.parent.mkdir(parents=True, exist_ok=True)

original = pd.read_excel(input, sheet_name=1)[[' ', 'Japanese', 'OriginalFileName']].fillna('')
mod = pd.read_excel(input, sheet_name='mod')[[' ', 'Japanese', 'OriginalFileName']].fillna('')
correct = mod.loc[lambda d: d['Japanese']!=original['Japanese']]
d = {x[0]: {'Japanese': x[1], 'OriginalFileName': x[2]} for i, x in correct.iterrows()}

with output.open('w', encoding='utf-8') as j:
    json.dump(d, j, ensure_ascii=False)
