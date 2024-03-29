# Corrected Japanese Text of Valheim

https://www.nexusmods.com/valheim/mods/1511/

## Installation / インストール

1. install the latest [BepInExPack Valheim](https://valheim.thunderstore.io/package/denikson/BepInExPack_Valheim/)
2. install the latest [Jotunn](https://www.nexusmods.com/valheim/mods/1138)
3. install this mod. You can find and download the latest binary from [Releases](https://github.com/Gedevan-Aleksizde/valheim-ja/releases)

You can also downlaod the standalone version which includes both of the two above dependencies. 

------

1. 最新の [BepInExPack Valheim](https://valheim.thunderstore.io/package/denikson/BepInExPack_Valheim/) をインストールしてください
2. 最新の [Jotunn](https://www.nexusmods.com/valheim/mods/1138) をインストールしてください.
3. この mod をインストールしてください. 右の [Releases](https://github.com/Gedevan-Aleksizde/valheim-ja/releases) から最新バージョンのバイナリを見つけることができます.

あるいは, 上記2つの依存mod を同梱した Standalone 版も用意しています. こちらは手順1, 2は不要です.

The following paragraph is the instruction for older versions (<1.0).  
以下は v1.0 より古いバージョンでのインストール方法です

1. Download the latest `resources.assets` file from [Release page](https://github.com/Gedevan-Aleksizde/valheim-ja/releases)
2. Overwrite the file with the downloaded one in  `valheim_Data/` in your Valheim installed directory.

上記リンク先に行くか, 以下を読んでください

1. 最新の `resources.assets` ファイルを[Release page](https://github.com/Gedevan-Aleksizde/valheim-ja/releases)からダウンロードする
2. Valheim インストールフォルダの `valheim_Data/` 内の同名のファイルを上書きする

## Dependencies for editor tools / 編集ツールの依存ソフト

If you want to edit the text on your own, you need the following programs:

自身でテキストを編集したい場合は以下のようなものが必要です:

* [UABE](https://github.com/DerPopo/UABE) or [UAAE](https://github.com/Igor55x/UAAE)
* Python > 3.9

    * pandas
    * openpyxl

## Usage / 使い方

* Valheim 本体が開発中なのでアップデートで動作しなくなる可能性がある
* 個人作業用スクリプトなので使用方法が複雑

1. UABE などで `resources.assets` ファイルの `localization`, `localization_extra` アセットをjson形式で取り出す.
1.  `python tools/import-text.py` で XLSX ファイルに出力
    * ファイルパスは引数で指定するか, `params.json` に書いておく
    * `$1` のような変数は正規表現で自動で検知し前後でスペースを挿入するので, 変数が文字化けする問題はほとんど自動的に解決される
    * `LATEST_VERSION`, `mod` シートは上書きされる
1. 手動で編集する
    * 以前のバージョンのテキストがあるのなら, `python tools/update-and-merge.py` を使うと更新差分がわかる
    * 元のテキストの ID がユニークではないことがあるので直接マージはしない仕様にした
    * `CORRECTED`, `MISSING`, といった列は変更理由を表すフラグ. 編集管理をしやすくするために用意しただけで必須ではない. 
1. `python tools/make-dict.py` で上記 XLSX での変更差分を dict 形式に出力する
	* 現状これ自体は作業に必要ではないが, 変更していない全テキストをgithubに上げるのは著作権的に良くないと思うので
1. `python tools/export-text.py` で UABE用の TXT ファイルに変換し, UABE で上書きする
    * "Import Dump" ボタンで上書き (Import Raw だと機能しない?)
    * UABE 以外を使っている場合は適当に変換プログラムを自作する


## Note / 注記

* [dict/](dict/) contains retranslated text as json
* [terms.json](terms.json) is not refered by any Python scripts. It's just my personal memo so as to translate text consistenytly.

* [dict/](dict/) には修正テキストがjson形式で含まれています.
* [terms.json](terms.json) はPythonスクリプトでは使用していません. 翻訳テキストの一貫性のための個人的な作業メモです.


## See Also / 関連

Mod の日本語化はこちら: https://github.com/Gedevan-Aleksizde/valheim-mod-jp
