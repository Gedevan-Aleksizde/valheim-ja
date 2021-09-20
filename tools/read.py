#! /usr/bin/env python 

import json
from pathlib import Path
from io import StringIO
import pandas as pd
import argparse

# TODO: how to extract localization texts from `resources.assets`

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--filenames', type=Path, nargs='+', help='file path(s) to parse', default=None)
parser.add_argument('--outdir', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')
rootdir = Path().cwd()
l10n_jsonpath = [rootdir.joinpath(x).expanduser() for x in [
    'localization-resources.assets-99-TextAsset.json',
    'localization_extra-resources.assets-100-TextAsset.json'
    ]
] if args.filenames is None else args.filenames
excelpath = rootdir.joinpath('l10n.xlsx').expanduser() if args.outdir is None else Path(args.outdir).joinpath('l10n.xlsx')
csvpath = rootdir.joinpath('l10n-native.csv').expanduser() if args.outdir is None else Path(args.outdir).joinpath('l10n-native.csv')
csvs = []
for x in l10n_jsonpath:
    with x.open("r") as f:
        tmp = pd.read_csv(StringIO(json.load(f)['0 TextAsset Base']['1 string m_Script']), encoding="utf-8").fillna('').rename(columns={'Context': ' '})
        count_without_blank = tmp.loc[lambda d: d['Japanese'].str.match('\$[0-9a-zA-Z]+')].shape[0]
        print(f"{x}: {tmp.shape[0]} entries included; {count_without_blank} blank-omitted entries are found.")
        csvs += [tmp.assign(OriginalFileName=x.name)]
    # In v0.202.19, l10n-extra text assets have field names ['Context', 'English', ..., 'Japanese', ...] while l10n text assets have ['', 'English', ..., 'Japanese', ...] 
    # variable symbols have `$` in prefix, so we can search by regex "\$[0-9a-zA-Z]+"
    # automaticalyy tagging

tab_l10n = pd.concat(csvs)
if(tab_l10n.shape[0] > 0):
    tab_l10n = (
        tab_l10n.assign(Japanese = lambda d: d['Japanese'].str.replace('(\$[0-9a-zA-Z]+)', ' \\1 ', regex=True).
        str.replace('^\s', '', regex=True).
        str.replace('\s$', '', regex = True).
        str.replace('\s{2,}', ' ', regex=True)
        )
    )
# quoting=1: csv.QUOTE_ALL
tab_l10n.to_csv(csvpath, index=False, encoding="utf-8", quoting=1)
# 手動編集の簡易さからエクセルに書く
# TODO: libre が重すぎるので PO ファイルとして出力したほうがいいか?
with pd.ExcelWriter(excelpath) as writer:  
    tab_l10n.to_excel(writer, sheet_name = "mod", index=False)
    tab_l10n.to_excel(writer, sheet_name = "v0.202.19", index=False)
