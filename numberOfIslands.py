import os
import sys
import time

import rasterio
import numpy as np
import random

sys.setrecursionlimit(100000)

class NumberOfIslands:
    def __init__(self, graph, algorithm="dfs", contiguity="rook", is_land=None, out=False, out_folder='data'):
        # TODO: check grid
        self.graph = graph
        self.height = graph[0].shape[0]
        self.width = graph[0].shape[1]
        self.visited = np.zeros(rs.shape)
        self.queue = [] # used for bfs

        self.neighbors_rook = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # N, E, S, W
        self.neighbors_queen = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (-1, 1), (0, -1), (-1, -1)]  # N, NE, E, SE, S, SW, W, NW
        
        self.algorithm = {"dfs": self.dfs, "bfs": self.bfs}[algorithm]
        self.contiguity = {"rook": self.neighbors_rook, "queen": self.neighbors_queen}[contiguity]

        self.out = out
        self.out_folder = out_folder
        self.out_options = {
            'driver': 'GTiff', 
            # 'driver': 'GJpg', 
            'dtype': 'uint8', 
            'nodata': None, 
            'width': self.width if (self.width % 2) == 0 else self.width-1, 
            'height': self.height if (self.height % 2) == 0 else self.height-1,
            'count': 3, 
            'crs': None, 
            'tiled': False, 
            'interleave': 'pixel', 
            'compress': 'lzw'
        }
        self.out_bool = True

        self.colors = {
            'cursor':  [205, 0, 0],
            # 'land':     [50, 250, 50],
            'land':     [250, 100, 50],
        }
        self.previous_color = [0, 0, 0]
        self.cursor = [
            (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0),  # N
            # (-1, 1),
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),   # E
            # (1, 1),
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),    # S
            # (-1, 1),
            (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6),  # W
            # (-1, -1)
        ]
        self.neighbors_previous_colors = [[0, 0, 0] for i in range(len(self.cursor))]
        self.print_index = 0

        if is_land is None:
            self.is_land = lambda r, g, b : r + g + b > 300
        else:
            self.is_land = is_land

    # def is_land(self, x, y):
    #     return True

    def print_grid(self):
        for r in self.graph:
            for c in r:
                print(str(c) + " ", end='')
            print("")
        print("\n\n")

    def write_raster(self):
        # if self.out_bool:
        rs, gs, bs = self.graph

        # with rasterio.open(f'{self.out_folder}/noi_{self.print_index:06}.jpg', 'w' , **self.out_options) as dst:
        with rasterio.open(f'{self.out_folder}/noi_{self.print_index:06}.tif', 'w' , **self.out_options) as dst:
            dst.write(rs.astype(rasterio.uint8), 1)
            dst.write(gs.astype(rasterio.uint8), 2)
            dst.write(bs.astype(rasterio.uint8), 3)

        self.print_index += 1

        self.out_bool = not self.out_bool

    def color_cursor(self, i, j):
        # save current color
        self.previous_color = [rs[i][j], gs[i][j], bs[i][j]]

        # color current cell
        r, g, b = self.colors['cursor']
        rs[i][j] = r
        gs[i][j] = g
        bs[i][j] = b

        for k, n in enumerate(self.cursor):
            n_r = i + n[0]
            n_c = j + n[1]
            if self.is_valid(n_r, n_c):
                self.neighbors_previous_colors[k] = [rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]]
                rs[n_r][n_c] = r
                gs[n_r][n_c] = g
                bs[n_r][n_c] = b

        self.write_raster()

        # reset cell's color
        r, g, b = self.previous_color
        rs[i][j] = r
        gs[i][j] = g
        bs[i][j] = b

        # reset neighbor's colors
        for k, n in enumerate(self.cursor):
            n_r = i + n[0]
            n_c = j + n[1]

            if self.is_valid(n_r, n_c):
                r, g, b = self.neighbors_previous_colors[k]
                rs[n_r][n_c] = r
                gs[n_r][n_c] = g
                bs[n_r][n_c] = b

    def is_valid(self, row, col):
        return (row >= 0) and (row < self.height) and (col >= 0) and (col < self.width)

    def dfs(self, row, col):
        rs, gs, bs = self.graph

        # land
        self.visited[row][col] = 1

        if self.out and (col % 4 == 0):
            self.color_cursor(row, col)

        for i, n in enumerate(self.contiguity):
            n_r = row + n[0]
            n_c = col + n[1]

            # if self.is_valid(n_r, n_c) and self.grid[n_r][n_c] == 1:
            if self.is_valid(n_r, n_c) and not self.visited[n_r][n_c]:
                # Case: land
                if self.is_land(rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]):
                    self.dfs(n_r, n_c)

                # Case: water (near land)
                else:
                    r, g, b = self.colors['land']
                    rs[n_r][n_c] = r
                    gs[n_r][n_c] = g
                    bs[n_r][n_c] = b

            # elif self.is_valid(n_r, n_c) and self.grid[n_r][n_c] == 0:
            #     self.grid[n_r][n_c] = ' '

    def bfs(self, row, col):
        rs, gs, bs = self.graph

        # land
        self.visited[row][col] = 1
        self.queue.append([row, col])

        while self.queue:
            s = self.queue.pop(0)

            if self.out and (s[1] % 4 == 0):
                self.color_cursor(s[0], s[0])

            for i, n in enumerate(self.contiguity):
                n_r = s[0] + n[0]
                n_c = s[1] + n[1]

                # if self.is_valid(n_r, n_c) and self.is_land(rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]) and not self.visited[n_r][n_c]:
                #     self.visited[n_r][n_c] = 1
                #     self.queue.append([n_r, n_c])

                if self.is_valid(n_r, n_c) and not self.visited[n_r][n_c]:
                    # Case: land
                    if self.is_land(rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]):
                        self.visited[n_r][n_c] = 1
                        self.queue.append([n_r, n_c])

                    # Case: water (near land)
                    else:
                        r, g, b = self.colors['land']
                        rs[n_r][n_c] = r
                        gs[n_r][n_c] = g
                        bs[n_r][n_c] = b

    def number_of_islands(self):

        # if not self.grid or not self.grid[0]:
        #     return 0
            
        row = self.height
        col = self.width
        count = 0

        rs, gs, bs = self.graph
        self.visited = np.zeros(rs.shape)

        
        
        for i in range(0, row):
            for j in range(0, col):

                if self.out and not self.visited[i][j] and (j % 20 == 0):  # only every 4 cells

                    self.color_cursor(i, j)

                # Case: Land
                # if self.grid[i][j] == 1:
                if self.is_land(rs[i][j], gs[i][j], bs[i][j]) and not self.visited[i][j]:
                    self.algorithm(i, j)
                    count += 1
                    

                # Case: Water (not near land) (OPTIONAL)
                # elif self.grid[i][j] == 0:
                #     self.grid[i][j] = ' '

                # print_grid(graph)
            
        return count

def is_land(r, g, b):
    b = not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170))
    # print(b)
    return b

with rasterio.open('hr_se_asia_720p.tif') as dataset:
    rs, gs, bs = dataset.read(
        # resampling=Resampling.bilinear
    )[0:3]

    # profile = dataset.profile
    # profile.update(dtype=rasterio.uint8, count=1, compress='lzw')


# is_land = lambda r, g, b : not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170))

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'data')



# t1 = time.perf_counter()
# noi = NumberOfIslands([rs, gs, bs], algorithm="dfs", is_land=is_land, out=False, out_folder=filename)
# print(f"Grid Size:\t\t{rs.shape[0]}x{rs.shape[1]} = {rs.shape[0] * rs.shape[1]}")
# print(f"Number of Islands:\t{noi.number_of_islands()}")
# print(f"Execution Time:\t\t{time.perf_counter() - t1}")

t1 = time.perf_counter()
noi = NumberOfIslands([rs, gs, bs], algorithm="bfs", is_land=is_land, out=True, out_folder=filename)
print(f"\nGrid Size:\t\t{rs.shape[0]}x{rs.shape[1]} = {rs.shape[0] * rs.shape[1]}")
print(f"Number of Islands:\t{noi.number_of_islands()}")
print(f"Execution Time:\t\t{time.perf_counter() - t1}\n")

# /Applications/ffmpeg -r 60 -f image2 -s 1920x1080 -i data/noi_%06d.tif -vcodec libx264 -crf 25  -pix_fmt yuv420p test.mp4