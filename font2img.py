import os
import glob
import argparse
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

CAPS = [chr(i) for i in range(65, 65 + 26)]

def pil2num(pil_img):
    num_img = np.asarray(pil_img)
    num_img.flags.writeable = True
    return num_img

def num2pil(num_img):
    pil_img = Image.fromarray(np.uint8(num_img))
    return pil_img

def convert_binary_img(pil_img, threshold=128):
    num_img = pil2num(pil_img)
    for row_i in range(len(num_img)):
        for col_i in range(len(num_img[0])):
            if num_img[row_i][col_i] < threshold:
                num_img[row_i][col_i] = 0
            else:
                num_img[row_i][col_i] = 255
    binary_pil_img = num2pil(num_img)
    return binary_pil_img

def get_offset(pil_img, normal_canvas_size):
    num_img = pil2num(pil_img)
    canvas_size = len(num_img)
    canvas_offset = canvas_size - normal_canvas_size
    margins = {}
    # top
    for i in range(canvas_size):
        for j in range(canvas_size):
            if num_img[i][j] != 255:
                margins['top'] = i
                break
        if 'top' in margins:
            break
    # bottom
    for i in range(canvas_size):
        for j in range(canvas_size):
            if num_img[canvas_size - i - 1][j] != 255:
                margins['bottom'] = i - canvas_offset
                break
        if 'bottom' in margins:
            break
    # left
    for j in range(canvas_size):
        for i in range(canvas_size):
            if num_img[i][j] != 255:
                margins['left'] = j
                break
        if 'left' in margins:
            break
    # right
    for j in range(canvas_size):
        for i in range(canvas_size):
            if num_img[i][canvas_size - j - 1] != 255:
                margins['right'] = j - canvas_offset
                break
        if 'right' in margins:
            break
    x_offset = int((margins['right'] - margins['left']) / 2)
    y_offset = int((margins['bottom'] - margins['top']) / 2)
    offsets = (x_offset, y_offset)

    is_tb_maximum = margins['top'] + margins['bottom'] <= 0
    is_lr_maximum = margins['right'] + margins['left'] <= 0
    is_maximum = is_tb_maximum or is_lr_maximum
    return offsets, is_maximum

def draw_char(char, font_path, canvas_size, font_size, offsets=(0, 0)):
    font = ImageFont.truetype(font_path, size=font_size)
    img = Image.new('L', (canvas_size, canvas_size), 255)
    draw = ImageDraw.Draw(img)
    draw.text(offsets, char, 0, font=font)
    img = convert_binary_img(img)
    return img

def draw_char_center(char, font_path, canvas_size, font_size, check_maximum=False):
    no_offset_img = draw_char(char, font_path, canvas_size + 20, font_size)
    offsets, is_maximum = get_offset(no_offset_img, canvas_size)
    img = draw_char(char, font_path, canvas_size, font_size, offsets)
    if check_maximum:
        return img, is_maximum
    else:
        return img

def draw_char_maximum(char, font_path, canvas_size, **kwargs):
    font_size = canvas_size
    while True:
        img, is_maximum = draw_char_center(char, font_path, canvas_size, font_size, check_maximum=True)
        if is_maximum:
            break
        font_size += 1
    return img

def get_ext_filepaths(dirpath, exts):
    dirpath = os.path.normpath(dirpath)
    filepaths = []
    for ext in exts:
        filepaths_tmp = glob.glob(dirpath + '/*.' + ext)
        filepaths.extend(filepaths_tmp)
    return filepaths

def font2img(src_font_path, dst_dir_path, canvas_size, font_size, is_center=True, is_maximum=False, output_ext='png'):
    if not os.path.exists(dst_dir_path):
        os.mkdir(dst_dir_path)
    if is_maximum:
        draw_char_func = draw_char_maximum
    elif is_center:
        draw_char_func = draw_char_center
    else:
        draw_char_func = draw_char
    font_paths= get_ext_filepaths(src_font_path, ['ttf', 'ttc', 'otf'])
    for font_path in font_paths:
        dst_img_dir_path = \
            os.path.join(dst_dir_path, os.path.basename(os.path.splitext(font_path)[0]))
        if not os.path.exists(dst_img_dir_path):
            os.mkdir(dst_img_dir_path)
        for c in CAPS:
            img = draw_char_func(char=c, font_path=font_path, canvas_size=canvas_size, font_size=font_size)
            if img:
                img.save(os.path.join(dst_img_dir_path, c + '.'  + output_ext))
        print ('proccessed {0}'.format(font_path))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='convert ttf/otf into png/jpg/etc')
    parser.add_argument('src_dir_path', action='store', type=str, help='Directory path where source files are located.')
    parser.add_argument('dst_dir_path', action='store', type=str, help='Directory path of destination.')
    parser.add_argument('canvas_size', action='store', type=int, help='Canvas size')
    parser.add_argument('--not-centering', dest='is_center', action='store_false', help='Centering or not')
    parser.add_argument('-m', '--maximum', dest='is_maximum', action='store_true', help='Maximum or not')
    parser.add_argument('-f', '--font-size', dest='font_size', action='store', type=int, help='Font point size')
    parser.add_argument('-e', '--ext', dest='ext', action='store', type=str, default='png', help='Output extention')
    args = parser.parse_args()
    if args.font_size == None:
        font_size = args.canvas_size
    else:
        font_size = args.font_size
    font2img(src_font_path=args.src_dir_path, \
             dst_dir_path=args.dst_dir_path, \
             canvas_size=args.canvas_size, \
             font_size=font_size, \
             is_center=args.is_center, \
             is_maximum=args.is_maximum, \
             output_ext=args.ext)
