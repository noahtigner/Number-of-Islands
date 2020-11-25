import os
import time
import rasterio

from number_of_islands import NumberOfIslands

water = set()
for i in range(14):

    with rasterio.open(f'in/water{i}.tif') as dataset:
        rw, gw, bw = dataset.read()[0:3]
        
        for i in range(0, rw.shape[0]):
            for j in range(0, rw.shape[1]):
                water.add((rw[i][j], gw[i][j], bw[i][j]))

def is_land_simple(r, g, b):
    # return (r>=20 or g>=20 or b>=20)
    return r>12

def is_land_comparison(r, g, b):
    # return not ((r, g, b) in water)
    return True

def is_land_classifier(r, g, b):
    # this could be an unsupervised classifier
    return True

def is_land(r, g, b):
    b1 = is_land_simple(r, g, b)
    b2 = is_land_comparison(r, g, b) 
    b3 = is_land_classifier(r, g, b)
    # print(f"{(r, g, b)} -> {b1, b2, b3}")
    return is_land_simple(r, g, b)# and is_land_comparison(r, g, b) and is_land_classifier(r, g, b)

def run_analysis(raster, algorithm, is_land, out, out_folder):
    start_time = time.perf_counter()
    noi = NumberOfIslands(raster, algorithm=algorithm, is_land=is_land, out=out, out_folder=out_folder)
    print(f"\nGrid Size:\t\t{rs.shape[0]}x{rs.shape[1]} = {rs.shape[0] * rs.shape[1]}")
    count = noi.number_of_islands()
    # if count:
    print(f"Number of Islands:\t{count}")
    print(f"Execution Time:\t\t{time.perf_counter() - start_time}\n")

with rasterio.open('in/nasa_blueMarble_240p2.tiff') as dataset:
    rs, gs, bs = dataset.read()[0:3]

filename = os.path.join(os.path.dirname(__file__), 'out')

# print(f"{rs[0][0]}, {gs[0][0]}, {bs[0][0]}")
run_analysis(raster=[rs, gs, bs], algorithm="bfs", is_land=is_land, out=True, out_folder=filename)

# /Applications/ffmpeg -r 60 -f image2 -s 1920x1080 -i data/noi_%06d.tif -vcodec libx264 -crf 25  -pix_fmt yuv420p test.mp4
# /Applications/ffmpeg -r 240 -f image2 -s 1920x1080 -i out/noi_%06d.tif -filter:v "setpts=0.25*PTS" -vcodec libx264 -crf 15 -pix_fmt yuv420p test.mp4