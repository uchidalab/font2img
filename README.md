# font2img
フォントファイルから画像生成．

研究室で受け継がれてたものが古くて改造しにくかったので，
PythonのPillowで試しに作ってみたものです．

## Requirement
- Python 3
- Pillow
- Numpy
- ProgressBar2

```
pip3 install pillow numpy progressbar2
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
|`-v (--verbose)`|フォント毎の進捗表示．最大化するときつけると良いかも．|False|

## Features
- 入力txtはただのtxtファイルでOK．A-Zを出力したいなら`ABCDEFGHIJKLMNOPQRSTUVWXYZ`と書く．
  - 重複していても1回しか生成されない．
  - スペース，タブ，改行などは無視される．
- 出力のディレクトリ構造は，各フォントのディレクトリが生成され，その中にA.png, B.png...のように保存される．
  - ただし，ファイル名として不適切な文字は{その文字コード}.pngとなる．
- フォントに該当の文字が含まれていない場合，その情報が{出力ディレクトリ}/failure_chars.txtに出力される．

## TODO
- 最大化が遅い．アルゴリズム変えてもっと高速化できるはず．
- failure_chars.txtは追記形式．なので，同じ出力先で数回実行しても追記されるだけ．更新されるようにしたい．

## References
- [zi2zi](https://github.com/kaonashi-tyc/zi2zi)のfont2img.py
