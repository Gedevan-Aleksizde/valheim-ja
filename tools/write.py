#! /usr/bin/env python 
# convert xlsx to json
import json
from pathlib import Path
from io import StringIO
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--filename', type=Path, help='file path(s) to parse', default=None)
parser.add_argument('--outdir', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')

rootdir = Path().cwd()
excelpath = rootdir.joinpath('l10n.xlsx').expanduser() if args.filename is None else Path(args.flename)
csvpath = excelpath.parent.joinpath('l10n-mod.csv').expanduser()
outputdir = rootdir.joinpath('output') if args.outdir is None else Path(args.outdir)
if not outputdir.exists():
    outputdir.parent.mkdir(parents=True, exist_ok=True)
    print(f"{outputdir} doesn't exist. Created now.")

tab_l10n = pd.read_excel(excelpath, sheet_name='mod').fillna('')
# export CSV to compare the native text
tab_l10n.to_csv(csvpath, index=False, encoding="utf-8", quoting=1)

outputname = {x.split('.')[0].split('-')[0] : outputdir.joinpath(x).expanduser().with_suffix('.txt') for x in tab_l10n.OriginalFileName.unique()}
    

for out_entry, out_path in outputname.items():
    tmp = tab_l10n.loc[lambda d: [Path(out_path).with_suffix('').name==Path(x).with_suffix('').name for x in d['OriginalFileName']]].drop(columns=['OriginalFileName', 'Editted'])
    if out_entry=='localization_extra':
        tmp = tmp.rename(columns={' ': 'Context'})
    # Some entries has linebreak letters
    # # TODO: But does \r make sence?
    l10n_data = tmp.to_csv(index=False, encoding="utf-8", quoting=1, line_terminator=r"\n")
    l10n_data = l10n_data.replace('\r', r'\r').replace('\n', r'\n')
    # TODO: "import json" is useless in UABE...
    txt = f"""0 TextAsset Base
    1 string m_Name = "{out_entry}"
    """ + f' 1 string m_Script = "{l10n_data}"\n'
    with out_path.open('w') as f:
        f.writelines(txt)
        print(f'{out_entry} has {tmp.shape[0]} entries and is saved at {out_path}')
