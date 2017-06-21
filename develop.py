import font2img
import numpy as np

no_offset_img = font2img.draw_char('A', '/home/abekoh/Research/convert_font/src/NotoSansCJKjp-Regular.otf', 512, 256, offsets=(0, 0))

num_img = font2img.pil2num(no_offset_img)

print(num_img.shape)

a = np.where(num_img != 255)

print(a[0].shape, a[1].shape)
