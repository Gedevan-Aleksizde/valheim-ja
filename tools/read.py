import json
from pathlib import Path
from io import StringIO
import pandas as pd

# NOT in tools/
rootdir = Path().cwd()

l10n_jsonpath = [rootdir.joinpath(x).expanduser() for x in [
    'localization-resources.assets-99-TextAsset.json',
    'localization_extra-resources.assets-100-TextAsset.json'
]]
excelpath = rootdir.joinpath('l10n.xlsx').expanduser()
csvpath = rootdir.joinpath('l10n-native.csv').expanduser()
csvs = []
for x in l10n_jsonpath:
    with x.open("r") as f:
        tmp = pd.read_csv(StringIO(json.load(f)['0 TextAsset Base']['1 string m_Script']), encoding="utf-8").fillna('').rename(columns={'Context': ' '})
        csvs += [tmp.assign(OriginalFileName=x.name)]
    # In v0.202.19, l10n-extra text assets have field names ['Context', 'English', ..., 'Japanese', ...] while l10n text assets have ['', 'English', ..., 'Japanese', ...] 
    # variable symbols have `$` in prefix, so we can search by regex "\$[0-9a-zA-Z]+"
    # automaticalyy tagging

tab_l10n = pd.concat(csvs)
count = tab_l10n.loc[lambda d: d['Japanese'].str.match('\$[0-9a-zA-Z]+')].shape[0]
print(f"{count} invalid tagging are found")
if(count > 0):
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