# font2img
フォントファイルから画像生成．

研究室で受け継がれてたものが古くて改造しにくかったので，
PythonのPillowで試しに作ってみたものです．

## Requirement
- Python 3
- Pillow
- Numpy
- tqdm

```
pip3 install pillow numpy tqdm
```

## Usage
```
python3 font2img.py {フォントファイル(ttf, ttc, otf, otc)が入ったディレクトリ} {画像化したい文字列が入ったtxt} {出力ディレクトリ(自動生成)} [options]
```
### Options
|オプションコマンド|効果|デフォルト値|
|:-|:-|:-|
|`-c (--canvas_size) {キャンバスサイズ}`|キャンバスの一辺のサイズを指定．単位はpixel．|256|
|`-f (--font_size) {フォントサイズ}`|フォントサイズ指定．単位はpt．指定しなければ適当に決まる．|canvas_size * 0.75|
|`-e (--ext) {拡張子}`|出力する画像の拡張子．|png|
|`--not-centering`|センタリングしないように．|False|
|`-m (--maximum)`|キャンバスサイズいっぱいに最大化．処理遅め．|False|
|`-b (--binary)`|2値画像として保存．|False|
|`-u (--unicode)`|画像のファイル名をUnicodeの数値として保存．|False|
|`--by-char`|階層構造を変更．サブディレクトリ名が文字名に.|False|

## Features
- 入力txtはただのtxtファイルでOK．A-Zを出力したいなら`ABCDEFGHIJKLMNOPQRSTUVWXYZ`と書く．
  - 重複していても1回しか生成されない．
  - スペース，タブ，改行などは無視される．
- 出力のディレクトリ構造は，
  - デフォルトでは，各フォント名のディレクトリが生成され，その中にA.png, B.png...のように保存される．
  - `--by-char`オプションをつけると，文字名がディレクトリ，その中にArial.pngのように保存される．
- 文字名について，
  - ファイル名として不適切な文字は{その文字コード}となる．(`?:/"`などが該当．)
  - アルファベットの大文字と小文字が存在する場合，大文字のほうはA_のようにアンダースコアが付与される．
- 描画に失敗した場合，その情報が{出力ディレクトリ}/failure.txtに出力される．
  - ある文字がフォントに含まれていなかった(真っ白だった)場合のエラーは`white`，該当する文字も出力
  - すべての文字が同じになった(ttfの異常？ [#16](https://github.com/uchidalab/font2img/issues/16))場合のエラーは`same`

## TODO
- 最大化が遅い．アルゴリズム変えてもっと高速化できるはず．
- failure.txtは追記形式．なので，同じ出力先で数回実行しても追記されるだけ．更新されるようにしたい．

## References
- [zi2zi](https://github.com/kaonashi-tyc/zi2zi)のfont2img.py
