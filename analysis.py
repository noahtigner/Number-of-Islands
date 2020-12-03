import os
import time
import rasterio

from number_of_islands import NumberOfIslands

def is_land_simple(r, g, b):
    """
    simple classifier uses redness of a cell

    args:   (r, g, b), the 3 band values for a given cell (need not be r, g, b)
    effects: 
    returns: boolean
    """
    return r > 12

def is_land_comparison(r, g, b):
    # compare pixel to pixels known to be water
    # water = set()
    # for i in range(4):
    #     with rasterio.open(f'in/water{i}.tif') as dataset:
    #         rw, gw, bw = dataset.read()[0:3]
    #         for i in range(0, rw.shape[0]):
    #             for j in range(0, rw.shape[1]):
    #                 water.add((rw[i][j], gw[i][j], bw[i][j]))
    # return not ((r, g, b) in water)
    return True

def is_land_classifier(r, g, b):
    # this could be an unsupervised classifier
    return True

def is_land(r, g, b):
    """
    decide if a pixel fits the definition of land

    args:   (r, g, b), the 3 band values for a given cell (need not be r, g, b)
    effects: 
    returns: boolean
    """

    b1 = is_land_simple(r, g, b)
    # b2 = is_land_comparison(r, g, b) 
    # b3 = is_land_classifier(r, g, b)
    return b1 # and b2 and b3

def run(raster, algorithm, is_land, out, out_folder, prints=True):
    """
    a helper function for running the analysis

    args:   raster, algorithm, is_land, out, out_folder, prints
    effects: prints output (if prints=True), creates rasters (if out=True)
    returns: (elapsed time, number of islands)
    """

    start_time = time.perf_counter()
    noi = NumberOfIslands(raster, algorithm=algorithm, is_land=is_land, out=out, out_folder=out_folder)
    if prints:
        print(f"\nGrid Size:\t\t{rs.shape[0]}x{rs.shape[1]} = {rs.shape[0] * rs.shape[1]}")
        print(f"Algorithm:\t\t{algorithm}")
    
    try:
        count = noi.number_of_islands()
        elapsed = round(time.perf_counter()-start_time, 2)
        if prints:
            print(f"Number of Islands:\t{count}")
            print(f"Execution Time:\t\t{elapsed}\n")
        return (elapsed, count)
    except:
        return (None, None)

################

filename = os.path.join(os.path.dirname(__file__), 'out')

# list of input rasters
rasters = ["in/nasa_blueMarble_240p.tiff", "in/nasa_blueMarble_480p.tiff", "in/nasa_blueMarble_720p.tiff"]

# the three search algorithms implemented
algorithms = ["dfs", "dfs'", "bfs"]

# read in 3 bands from input raster
with rasterio.open(rasters[1]) as dataset:
    rs, gs, bs = dataset.read()[0:3]

# simple example of module use
# run(raster=[rs, gs, bs], algorithm="bfs", is_land=is_land, out=False, out_folder=filename)

# complec example of module use - for comparing algorithms
# for each raster, print the elapsed time of each algorithm
for raster in rasters:
    times = {algo: [] for algo in algorithms}

    with rasterio.open(raster) as dataset:
        rs, gs, bs = dataset.read()[0:3]

    for trial in range(5):  # 5 trials per algorithm per raster
        for algo in algorithms:
            (e, n) = run(raster=[rs, gs, bs], algorithm=algo, is_land=is_land, out=False, out_folder=filename, prints=False)
            times[algo].append(e)   # add trial time for that algorithm for that raster

    print(f"{raster}:\t{times}")    # print trial times for all algorithms for this raster
