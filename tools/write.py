#! /usr/bin/env python 
# convert xlsx to json
import json
from pathlib import Path
from io import StringIO
import pandas as pd

rootdir = Path().cwd()
excelpath = rootdir.joinpath('l10n.xlsx').expanduser()
csvpath = rootdir.cwd().joinpath('l10n-mod.csv').expanduser()
outputpath = [rootdir.joinpath(f'output/{x}').expanduser() for x in [
    'localization-resources.assets-99-TextAsset.txt',
    'localization_extra-resources.assets-100-TextAsset.txt'
]]

tab_l10n = pd.read_excel(excelpath, sheet_name='mod').fillna('')
# export CSV to compare the native text
tab_l10n.to_csv(csvpath, index=False, encoding="utf-8", quoting=1)

tab_l10n.loc[lambda d: [Path(x).with_suffix('').name==Path('localization_extra-resources.assets-100-TextAsset.txt').with_suffix('') for x in d['OriginalFileName']]].drop(columns=['OriginalFileName'])
[Path(x).with_suffix('').name for x in tab_l10n.OriginalFileName[1:10]]

for output in outputpath:
    tmp = tab_l10n.loc[lambda d: [Path(output).with_suffix('').name==Path(x).with_suffix('').name for x in d['OriginalFileName']]]
    print(f'{output} has {tmp.shape[0]} entries.')
    if output=='localization_extra-resources.assets-100-TextAsset.txt':
        tmp = tmp.rename(columns={' ': 'Context'})
    # Some entries has linebreak letters
    # # TODO: But does \r make sence?
    l10n_data = tmp.to_csv(index=False, encoding="utf-8", quoting=1, line_terminator=r"\n")
    l10n_data = l10n_data.replace('\r', r'\r').replace('\n', r'\n')
    # TODO: "import json" is useless...
    txt = """0 TextAsset Base
    1 string m_Name = "localization"
    """ + f' 1 string m_Script = "{l10n_data}"\n'

    if not x.parent.exists():
        output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w') as f:
        f.writelines(txt)
