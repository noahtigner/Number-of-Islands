import os
import sys
import time

import rasterio
import numpy as np
import random

from numberOfIslands import NumberOfIslands

def is_land(r, g, b):
    return not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170))

with rasterio.open('hr_se_asia_240p.tif') as dataset:
    rs, gs, bs = dataset.read()[0:3]

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'out')



start_time = time.perf_counter()
noi = NumberOfIslands([rs, gs, bs], algorithm="bfs", is_land=is_land, out=False, out_folder=filename)
print(f"\nGrid Size:\t\t{rs.shape[0]}x{rs.shape[1]} = {rs.shape[0] * rs.shape[1]}")
print(f"Number of Islands:\t{noi.number_of_islands()}")
print(f"Execution Time:\t\t{time.perf_counter() - start_time}\n")

# /Applications/ffmpeg -r 60 -f image2 -s 1920x1080 -i data/noi_%06d.tif -vcodec libx264 -crf 25  -pix_fmt yuv420p test.mp4