#! /usr/bin/env python 
#
# l10n.xlsx のオリジナルテキストのシートと, mod シートを比べ, 変更のあるものを抜き出しjsonにする
#

import json
from pathlib import Path
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--filename', type=Path, help='file path(s) to parse', default=None)
parser.add_argument('--sheet', type=str, help='sheet name to read', default='mod')
parser.add_argument('--output', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')

input = Path('l10n.xlsx') if args.filename is None else args.filename
output = Path().cwd().joinpath('dict/correction.json') if args.output is None else args.output
if not output.parent.exists():
    output.parent.mkdir(parents=True, exist_ok=True)

with (Path(__file__).parent if '__file__' in locals() else Path().cwd().joinpath('tools')).joinpath('params.json').open('r') as fp:
    params = json.load(fp)
    print("""Valheim version: {VALHEIM_VERSION}\r\nTarget Language: {LANG}""".format(**params))

original = pd.read_excel(input, sheet_name=f"""v{params['VALHEIM_VERSION']}""")[[' ', params['LANG'], 'OriginalFileName']].fillna('')
mod = pd.read_excel(input, sheet_name=args.sheet)[[' ', params['LANG'], 'OriginalFileName']].fillna('')
correct = mod.loc[lambda d: d[params['LANG']]!=original[params['LANG']]]
d = {f: {x[0]: {params['LANG']: x[1]} for i, x in correct.loc[lambda d: d['OriginalFileName']==f].iterrows()} for f in correct['OriginalFileName'].unique()}


with output.open('w', encoding='utf-8') as j:
    json.dump(d, j, ensure_ascii=False, indent=2)
