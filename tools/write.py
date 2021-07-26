#! /usr/bin/env python 
# convert xlsx to json
import json
from pathlib import Path
from io import StringIO
import pandas as pd

rootdir = Path().cwd()
excelpath = rootdir.joinpath('l10n.xlsx').expanduser()
csvpath = rootdir.cwd().joinpath('l10n-mod.csv').expanduser()
txtpath = rootdir.cwd().joinpath('l10n-mod.txt').expanduser()

tab_l10n = pd.read_excel(excelpath).fillna('')
# export CSV to compare the previous one
tab_l10n.to_csv(csvpath, index=False, encoding="utf-8", quoting=1)

l10n_data = tab_l10n.to_csv(index=False, encoding="utf-8", quoting=1, line_terminator=r"\n")
# セル内に改行コードが入る場合もあるため
# TODO: しかし \r は意味があるのだろうか?
l10n_data = l10n_data.replace('\r', r'\r').replace('\n', r'\n')

txt = """0 TextAsset Base
 1 string m_Name = "localization"
""" + f' 1 string m_Script = "{l10n_data}"\n'

with txtpath.open('w') as f:
    f.writelines(txt)