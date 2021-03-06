import os
import time
import rasterio

from number_of_islands import NumberOfIslands

def is_land(r, g, b):
    # return not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170)) or (r>200 and g>200 and b>200) and ((r>=121 or r<=126) and (g>=135 or g<=140) and (b>=117 or b<=122))
    return not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170)) or (r>200 and g>200 and b>200) and ((r>=121 or r<=126) and (g>=135 or g<=140) and (b>=117 or b<=122))

def run_analysis(raster, algorithm, is_land, out, out_folder):
    start_time = time.perf_counter()
    noi = NumberOfIslands(raster, algorithm=algorithm, is_land=is_land, out=out, out_folder=out_folder)
    print(f"\nGrid Size:\t\t{rs.shape[0]}x{rs.shape[1]} = {rs.shape[0] * rs.shape[1]}")
    count = noi.number_of_islands()
    if count:
        print(f"Number of Islands:\t{count}")
        print(f"Execution Time:\t\t{time.perf_counter() - start_time}\n")

with rasterio.open('in/hr_se_asia_240p.tif') as dataset:
    rs, gs, bs = dataset.read()[0:3]

filename = os.path.join(os.path.dirname(__file__), 'out')

# print(f"{rs[0][0]}, {gs[0][0]}, {bs[0][0]}")
run_analysis(raster=[rs, gs, bs], algorithm="bfs", is_land=is_land, out=True, out_folder=filename)

# /Applications/ffmpeg -r 60 -f image2 -s 1920x1080 -i data/noi_%06d.tif -vcodec libx264 -crf 25  -pix_fmt yuv420p test.mp4
# /Applications/ffmpeg -r 240 -f image2 -s 1920x1080 -i out/noi_%06d.tif -filter:v "setpts=0.25*PTS" -vcodec libx264 -crf 15 -pix_fmt yuv420p test.mp4