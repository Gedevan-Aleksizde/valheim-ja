#! /usr/bin/env python 
# udpate TextAsset(s) dump file with corrected dictionary (json) and export them as new dump files.
# correctio.json の修正リストから UABE で上書きできるようなテキスト形式のファイルをエクスポートする
import json
from pathlib import Path
from io import StringIO
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--textdir', type=Path, help='file path(s) to parse', default=None)
parser.add_argument('--dictdir', type=Path, help='file path(s) to parse', default=None)
parser.add_argument('--outdir', type=Path, help='output directory', default=None)
args = parser.parse_args(None if __name__ == '__main__' else '')

with (Path(__file__).parent if '__file__' in locals() else Path().cwd().joinpath('tools')).joinpath('params.json').open('r') as fp:
    params = json.load(fp)
    print("""Valheim version: {VALHEIM_VERSION}\r\nTarget Language: {LANG}""".format(**params))

rootdir = Path().cwd()
textfiles = rootdir.glob('original-text/*.json') if args.textdir is None else Path(args.dictdir).glob('*.json')
dictfiles = rootdir.glob('dict/*.json') if args.dictdir is None else Path(args.dictdir).glob('*.json')
outdir = rootdir.joinpath('output') if args.outdir is None else Path(args.outdir)

if not outdir.exists():
    outdir.parent.mkdir(parents=True, exist_ok=True)
    print(f"{outdir} doesn't exist. Created now.")

dicts = {}
for x in dictfiles:
    with x.open("r") as f:
        dicts.update(json.load(f))

for x in textfiles:
    out_fname = x.with_suffix('.txt').name
    out_entry = x.with_suffix('').name.split('-')[0]     
    with x.open("r") as basefile:
        tmp = pd.read_csv(StringIO(json.load(basefile)['0 TextAsset Base']['1 string m_Script']), encoding="utf-8").fillna('').rename(columns={'Context': ' '})
    count_without_blank = tmp.loc[lambda d: d['Japanese'].str.match('\$[0-9a-zA-Z]+')].shape[0]
    print(f"{x}: {tmp.shape[0]} entries included; {count_without_blank} blank-omitted entries are modified.")
    if(tmp.shape[0] > 0):
        tmp = (
            tmp.assign(Japanese = lambda d: d['Japanese'].str.replace('(\$[0-9a-zA-Z]+)', ' \\1 ', regex=True).
            str.replace('^\s', '', regex=True).
            str.replace('\s$', '', regex = True).
            str.replace('\s{2,}', ' ', regex=True)
            )
        )
        tmp = tmp.set_index(' ')
        tmp_dict = pd.DataFrame([(k, v[params['LANG']]['text']) for k, v in dicts[x.name].items()], columns=[' ', params['LANG']]).set_index(' ')
        tmp[params['LANG']].update(tmp_dict[params['LANG']])
        tmp = tmp.reset_index() # What a messy API!
        if out_entry=='localization_extra':
            tmp = tmp.rename(columns={' ': 'Content'})
        print(f'{tmp_dict.shape[0]} entries updated.')
        raw_text = tmp.to_csv(index=False, encoding="utf-8", quoting=1, line_terminator=r"\n")
        raw_text = raw_text.replace('\r', r'\r').replace('\n', r'\n')
        txt = f"""0 TextAsset Base
        1 string m_Name = "{out_entry}"
        """ + f' 1 string m_Script = "{raw_text}"\n'
        with outdir.joinpath(out_fname) as writeto:
            writeto.open('w').writelines(txt)
            print(f'{out_entry} has {tmp.shape[0]} entries and is saved at {writeto}')
