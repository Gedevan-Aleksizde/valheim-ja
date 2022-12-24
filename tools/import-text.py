#! /usr/bin/env python 

# read localization TextAsset(s) dump file (extracted by UABE or UAAE) and export as .xlsx 

import json
from pathlib import Path
from io import StringIO
import pandas as pd
import argparse

# TODO: how to automatically extract and overwite localization texts from `resources.assets`


with (Path(__file__).parent if '__file__' in locals() else Path().cwd().joinpath('tools')).joinpath('params.json').open('r') as fp:
    params = json.load(fp)
    print("""Valheim version: {LATEST_VERSION}\r\nTarget Language: {LANG}""".format(**params))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--filenames', type=Path, nargs='+', help='file path(s) to parse', default=None)
parser.add_argument('--outdir', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')
rootdir = Path().cwd()
l10n_jsonpath = [rootdir.joinpath(f'original-text/v{params["LATEST_VERSION"]}/{x}').expanduser() for x in [
    'localization-resources.assets-99.json',
    'localization_extra-resources.assets-100.json'
    ]
] if args.filenames is None else args.filenames
excelpath = rootdir.joinpath(params['l10n']).expanduser() if args.outdir is None else Path(args.outdir).joinpath(params['l10n'])
csvpath = rootdir.joinpath('l10n-native.csv').expanduser() if args.outdir is None else Path(args.outdir).joinpath('l10n-native.csv')
csvs = []
for x in l10n_jsonpath:
    with x.open("r", encoding="utf-8") as f:
        tmp = json.load(f)['0 TextAsset Base']
        field_name = tmp['1 string m_Name']
        tmp = pd.read_csv(StringIO(tmp['1 string m_Script']), index_col=False)  # [,]"English","Swedish",...
        tmp = tmp.rename(
            columns={'Context': '', 'Unnamed: 0': ' '}
        ).fillna('')
        # tmp = pd.read_csv(StringIO(json.load(f)['0 TextAsset Base']['1 string m_Script']), encoding="utf-8").fillna('').rename(columns={'Context': ' '})
        count_without_blank = tmp.loc[lambda d: d[params['LANG']].str.match('\$[0-9a-zA-Z]+')].shape[0]
        print(f"{x}: {tmp.shape[0]} entries included; {count_without_blank} blank-omitted entries are found.")
        csvs += [tmp.assign(OriginalFileName=x.name)]
    # In v0.202.19, l10n-extra text assets have field names ['Context', 'English', ..., 'Japanese', ...] while l10n text assets have ['', 'English', ..., 'Japanese', ...] 
    # variable symbols have `$` in prefix, so we can search by regex "\$[0-9a-zA-Z]+"
    # automaticalyy tagging

tab_l10n = pd.concat(csvs)
if(tab_l10n.shape[0] > 0):
    tab_l10n_blank = (
        tab_l10n.assign(**{params['LANG']: lambda d: d[params['LANG']].str.replace('(\$[0-9a-zA-Z]+)', ' \\1 ', regex=True).
        str.replace('^\s', '', regex=True).
        str.replace('\s$', '', regex = True).
        str.replace('\s{2,}', ' ', regex=True)
        })
    )
output_cols = [' ', 'English', 'Swedish', 'Japanese', 'OriginalFileName']
# quoting=1: csv.QUOTE_ALL
tab_l10n_blank[output_cols].to_csv(csvpath, index=False, encoding="utf-8", quoting=1)
# 手動編集の簡易さからエクセルに書く
# TODO: libre が重すぎるので PO ファイルとして出力したほうがいいか?
with pd.ExcelWriter(excelpath) as writer: 
    tab_l10n[output_cols].to_excel(writer, sheet_name = f"v{params['LATEST_VERSION']}", index=False, encoding="utf-8")
    tab_l10n_blank[output_cols].to_excel(writer, sheet_name = "mod", index=False, encoding="utf-8")

with Path(f'''Valheim_{params['LATEST_VERSION']}@{params['LANG']}.po''').open('w', encoding='utf-8') as f:
    f.write(
        '''
"Last-Translator: Katagiri, Satoshi <katagiri.stsh@gmail.com>"
"Language-Team: None"
"Language: ja"
"MIME-Version: 1.0"
"Content-Type: text/plain; charset=UTF-8"
"Content-Transfer-Encoding: 8bit"
    ''');
    for row in tab_l10n.iterrows():
        f.write(f'''msgid "{row[1]['English']}"\n''')
        f.write(f'''msgstr "{row[1][params['LANG'].capitalize()]}"\n\n''')
