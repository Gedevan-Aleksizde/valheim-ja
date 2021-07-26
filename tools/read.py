import json
from pathlib import Path
from io import StringIO
import pandas as pd

# NOT in tools/
rootdir = Path().cwd()
jsonpath = rootdir.joinpath('localization-resources.assets-99-TextAsset.json').expanduser()
excelpath = rootdir.joinpath('l10n.xlsx').expanduser()
csvpath = rootdir.joinpath('l10n-native.csv').expanduser()

with jsonpath.open("r") as f:
    l10n = json.load(f)
    tab_l10n = pd.read_csv(StringIO(l10n['0 TextAsset Base']['1 string m_Script']), encoding="utf-8").fillna('')

tab_l10n.info()
tab_l10n[[' ', 'English', 'Japanese']]

tab_l10n.loc[lambda d: d['Japanese'].str.contains("\$[0-9a-zA-Z]+"), 'Japanese']

# tagging しないと変数が置き換えられない
tab_l10n = tab_l10n.assign(
    Japanese = lambda d: d['Japanese'].str.replace(
        '(\$[0-9a-zA-Z]+)', ' \\1 ', regex=True
    ).str.replace(
        '^\s', '', regex=True
    ).str.replace(
        '\s$', '', regex = True
    ).str.replace(
        '\s{2,}', ' ', regex=True
    )
)
# quoting=1: csv.QUOTE_ALL
tab_l10n.to_csv(csvpath, index=False, encoding="utf-8", quoting=1)
# 手動編集の簡易さからエクセルに書く
# TODO: libre が重すぎるので PO ファイルとして出力したほうがいいか?
with pd.ExcelWriter(excelpath) as writer:  
    tab_l10n.to_excel(writer, sheet_name = "mod", index=False)
    tab_l10n.to_excel(writer, sheet_name = "v0.156.2", index=False)