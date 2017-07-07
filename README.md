# convert_font
フォントファイルから画像生成．

前から研究室で受け継がれてたものが古くて改造しにくかったので新しいものを作ろうと，
PythonのPillowでフォント指定して描画できそうだったからやってみたものです．

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
python3 font2img.py {フォントファイル(ttf, ttc, otf)が入ったディレクトリ} {画像化したい文字が入ったtxt} {出力ディレクトリ(自動生成)} [options]
```
### Options
|オプションコマンド|効果|デフォルト値|
|:-|:-|:-|
|`-c (--canvas_size) {キャンバスサイズ}`|キャンバスの一辺のサイズを指定．|256|
|`-f (--font_size) {フォントサイズ}`|フォントサイズ指定．指定しなければ適当に決まる．|canvas_size * 0.75|
|`-e (--ext) {拡張子}`|出力する画像の拡張子．|png|
|`--not-centering`|センタリングしないように．|False|
|`-m (--maximum)`|キャンバスサイズいっぱいに最大化．ちょっと処理遅め．|False|
|`-b (--binary)`|2値画像として保存．|False|
|`-v (--verbose)`|フォント毎の進捗表示．最大化するときつけると良いかも．|False|

## Caution
- 入力txtに入ったスペース，タブ，改行などは無視される．
- 出力のディレクトリ構造は，各フォントのディレクトリが生成され，その中に`A.png`のように保存される．
  - ただし，ファイル名として不適切な文字は`{その文字コード}.png`となる．

## References
- [zi2zi](https://github.com/kaonashi-tyc/zi2zi)のfont2img.py
