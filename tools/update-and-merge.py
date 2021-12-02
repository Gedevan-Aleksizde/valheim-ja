# compare previous version and check if original (English) text is changed, then output the difference by another csv file

import json
from pathlib import Path
from io import StringIO
import pandas as pd
import numpy as np
import argparse

with (Path(__file__).parent if '__file__' in locals() else Path().cwd().joinpath('tools')).joinpath('params.json').open('r') as fp:
    params = json.load(fp)
    print("""Valheim version: {LATEST_VERSION}\r\nPrevious version:{PREVIOUS_VERSION}\r\nTarget Language: {LANG}""".format(**params))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--filenames', type=Path, nargs='+', help='file path(s) to parse', default=None)
parser.add_argument('--outdir', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')
rootdir = Path().cwd()

l10n_latest = pd.read_excel(rootdir.joinpath(params['l10n-olds']), sheet_name='v' + params['LATEST_VERSION'])
l10n_previous = pd.read_excel(rootdir.joinpath(params['l10n-olds']), sheet_name='v' + params['PREVIOUS_VERSION'])
l10n_latest.columns = ['ID'] + l10n_latest.columns[1:].tolist()
l10n_previous.columns = ['ID'] + l10n_previous.columns[1:].tolist()

l10n_latest = l10n_latest[['ID', 'English', params['LANG']]].drop_duplicates()
l10n_previous = l10n_previous[['ID', 'English', params['LANG']]].drop_duplicates()

l10n_latest[40:50].merge(l10n_previous[40:50], on='ID')

d_check_updated = l10n_latest.merge(
    l10n_previous,
    on=['ID']).assign(
        PREVIOUS_ENGLISH_TEXT=lambda d: np.where(d['English_x'] != d['English_y'], d['English_y'], '')
    ).rename(columns={f"{params['LANG']}_y": f"PREVIOUS_{params['LANG']}_TEXT"})
d_check_updated = d_check_updated.drop(columns=['English_x', 'English_y', f"{params['LANG']}_x"])

print(f"{(d_check_updated['PREVIOUS_ENGLISH_TEXT']!='').sum()} original text changed.")

d_check_updated.to_csv(rootdir.joinpath('check_updated.csv'))

# 普通に ID ダブってるので結合は無理. 手動で.
# l10n_latest = pd.read_excel(rootdir.joinpath(params['l10n-olds']), sheet_name=f"v{params['LATEST_VERSION']}")
# l10n_latest = l10n_latest.merge(d_check_updated, left_on=l10n_latest.columns[0], right_on='ID')
# with pd.ExcelWriter(rootdir.joinpath('l10n.xlsx')) as writer: 
#    l10n_latest.to_excel(writer, sheet_name = f"v{params['LATEST_VERSION']}", index=False)
#    l10n_latest.to_excel(writer, sheet_name = "mod", index=False)
