import os
import glob
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from progressbar import ProgressBar

INVISIBLE_CHARS = [' ', '　', '\n', '\r', '\t', '\a', '\b', '\f', '\v']
AVOIDED_CHARS = ['\\', '\0', '/', ':', '*', '?', '"', '<', '>', '|']
FONT_EXTS = ['ttf', 'ttc', 'otf']


class font2img():

    def __init__(self, src_font_dir_path, src_chars_txt_path, dst_dir_path, canvas_size, font_size, output_ext, is_center, is_maximum, is_binary, is_verbose):
        '''
        コンストラクタ
        '''
        self.src_font_dir_path = os.path.normpath(src_font_dir_path)
        self.src_chars_txt_path = os.path.normpath(src_chars_txt_path)
        self.dst_dir_path = os.path.normpath(dst_dir_path)
        self.canvas_size = canvas_size
        if font_size == 0:
            self.font_size = int(self.canvas_size * 0.75)
        else:
            self.font_size = font_size
        self.output_ext = output_ext
        self.is_verbose = is_verbose

        # 最大化，センタリング有り，センタリング無しで別の関数を使用
        if is_maximum:
            self._draw_char_func = self._draw_char_maximum
        elif is_center:
            self._draw_char_func = self._draw_char_center
        else:
            self._draw_char_func = self._draw_char

        # 2値画像の設定
        if is_binary:
            self.pil_mode = '1'
            self.white_value = 1
        else:
            self.pil_mode = 'L'
            self.white_value = 255

        if not os.path.exists(self.dst_dir_path):
            os.mkdir(self.dst_dir_path)

        self._get_font_paths()
        self._get_chars()

        self.failure_chars_txt = open(os.path.join(self.dst_dir_path, 'failure_chars.txt'), 'a')

    def __del__(self):
        self.failure_chars_txt.close()

    def _get_font_paths(self):
        '''
        フォントパスの取得
        FONT_EXTSに含まれる拡張子のファイルを全て取得
        '''
        self.font_paths = list()
        for ext in FONT_EXTS:
            tmp = glob.glob(self.src_font_dir_path + '/*.' + ext)
            self.font_paths.extend(tmp)

    def _get_chars(self):
        '''
        画像化する文字を取得
        '''
        with open(self.src_chars_txt_path) as chars_txt_file:
            readlines = chars_txt_file.readlines()
        str_chars = ''
        for line in readlines:
            str_chars += line
        self.chars = set(str_chars)
        # INVISIBLE_CHARSに含まれる不可視文字は除去
        for c in INVISIBLE_CHARS:
            if c in self.chars:
                self.chars.remove(c)

    def run(self):
        '''
        フォントの画像化実行
        '''
        for font_path in self.font_paths:
            print('proccessing {0}'.format(font_path))
            font_name = os.path.basename(os.path.splitext(font_path)[0])
            dst_img_dir_path = os.path.join(self.dst_dir_path, font_name)
            failure_chars = list()
            if not os.path.exists(dst_img_dir_path):
                os.mkdir(dst_img_dir_path)
            if self.is_verbose:
                progbar = ProgressBar(max_value=len(self.chars))
            for i, c in enumerate(self.chars):
                if self.is_verbose:
                    progbar.update(i + 1)
                img = self._draw_char_func(c, font_path, self.canvas_size, self.font_size)
                # 画像が真っ白，つまり画像化失敗した文字はfailure_charsに
                if self._is_white(img):
                    failure_chars.append(c)
                else:
                    # ファイル名に使えない文字(特にWindowsで)は文字コードに変換
                    if c in AVOIDED_CHARS:
                        c = ord(c)
                    img.save(os.path.join(dst_img_dir_path, '{}.{}'.format(c, self.output_ext)))
            if failure_chars:
                failure_chars.sort()
                print('failure characters: {}'.format(failure_chars))
                # 失敗したリストを書き込み．
                # TODO: 単純に追記にしているので，うまく更新できるように
                self.failure_chars_txt.write('{},{}\n'.format(font_name, failure_chars))

    def _draw_char(self, char, font_path, canvas_size, font_size, offsets=(0, 0)):
        '''
        PIL使ってフォントを描画
        '''
        font = ImageFont.truetype(font_path, size=font_size)
        img = Image.new(self.pil_mode, (canvas_size, canvas_size), self.white_value)
        draw = ImageDraw.Draw(img)
        draw.text(offsets, char, 0, font=font)
        return img

    def _draw_char_center(self, char, font_path, canvas_size, font_size, is_check_maximum=False):
        '''
        センタリングして描画
        '''
        no_offset_img = self._draw_char(char, font_path, canvas_size * 2, font_size)
        offsets, is_maximum = self._get_offset(no_offset_img)
        img = self._draw_char(char, font_path, canvas_size, font_size, offsets=offsets)
        if is_check_maximum:
            return img, is_maximum
        return img

    def _draw_char_maximum(self, char, font_path, canvas_size, font_size):
        '''
        最大化して描画
        '''
        # TODO: もっと高速かできるはず
        while True:
            img, is_maximum = self._draw_char_center(char, font_path, canvas_size, font_size, is_check_maximum=True)
            if is_maximum:
                break
            font_size += 1
        return img

    def _get_offset(self, pil_img):
        '''
        センタリングするためのオフセットを計算
        また，最大ならばis_maximum=Trueを返す
        '''
        num_img = self._pil2num(pil_img)
        canvas_size = len(num_img)
        canvas_offset = canvas_size - self.canvas_size
        margins = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
        # top
        for i in range(canvas_size):
            if False in (num_img[i] == self.white_value):
                margins['top'] = i
                break
        # bottom
        for i in range(canvas_size):
            if False in (num_img[canvas_size - i - 1] == self.white_value):
                margins['bottom'] = i - canvas_offset
                break
        # left
        for i in range(canvas_size):
            if False in (num_img[:, i] == self.white_value):
                margins['left'] = i
                break
        # right
        for i in range(canvas_size):
            if False in (num_img[:, canvas_size - i - 1] == self.white_value):
                margins['right'] = i - canvas_offset
                break
        x_offset = int((margins['right'] - margins['left']) / 2)
        y_offset = int((margins['bottom'] - margins['top']) / 2)
        offsets = (x_offset, y_offset)
        is_tb_maximum = margins['top'] + margins['bottom'] <= 0
        is_lr_maximum = margins['right'] + margins['left'] <= 0
        is_maximum = is_tb_maximum or is_lr_maximum
        return offsets, is_maximum

    def _is_white(self, pil_img):
        '''
        画像が真っ白かチェック
        真っ白ならTrueを返す
        '''
        num_img = self._pil2num(pil_img)
        if False not in (num_img[:] == self.white_value):
            return True
        return False

    def _pil2num(self, pil_img):
        '''
        PIL型からnumpy型に
        '''
        num_img = np.asarray(pil_img)
        # num_img.flags.writeable = True
        return num_img

    def _num2pil(self, num_img):
        '''
        numpy型からPIL型に
        '''
        pil_img = Image.fromarray(np.uint8(num_img))
        return pil_img


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert font files into image files. () is default value.')
    parser.add_argument('src_font_dir_path', action='store', type=str, help='Directory path where source files are located.')
    parser.add_argument('src_chars_txt_path', action='store', type=str, help='Characters txt path.')
    parser.add_argument('dst_dir_path', action='store', type=str, help='Directory path of destination.')
    parser.add_argument('-c', '--canvas_size', dest='canvas_size', action='store', type=int, default=256, help='Canvas-size[pixel]. (256)')
    parser.add_argument('-f', '--font-size', dest='font_size', action='store', type=int, default=0, help='Font-size[pt]. (canvas-size*0.75[pt])')
    parser.add_argument('-e', '--ext', dest='output_ext', action='store', type=str, default='png', help="Output images' extention. (png)")
    parser.add_argument('--not-centering', dest='is_center', action='store_false', help='Centerize or not. (True)')
    parser.add_argument('-m', '--maximum', dest='is_maximum', action='store_true', help='Maximize or not. (False)')
    parser.add_argument('-b', '--binary', dest='is_binary', action='store_true', help='Binarize or not. (False)')
    parser.add_argument('-v', '--verbose', dest='is_verbose', action='store_true', help='Show progress or not. (False)')
    args = parser.parse_args()
    f2i = font2img(src_font_dir_path=args.src_font_dir_path,
                   src_chars_txt_path=args.src_chars_txt_path,
                   dst_dir_path=args.dst_dir_path,
                   canvas_size=args.canvas_size,
                   font_size=args.font_size,
                   output_ext=args.output_ext,
                   is_center=args.is_center,
                   is_maximum=args.is_maximum,
                   is_binary=args.is_binary,
                   is_verbose=args.is_verbose)
    f2i.run()
