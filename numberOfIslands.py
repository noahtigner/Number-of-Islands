import rasterio
import numpy as np
import random

import sys
sys.setrecursionlimit(10000)

with rasterio.open('se_asia_xs.tif') as dataset:
    rs, gs, bs, t = dataset.read(
        # resampling=Resampling.bilinear
    )

    profile = dataset.profile
    profile.update(dtype=rasterio.uint8, count=1, compress='lzw')


# is_land = lambda r, g, b : not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170))

def is_land(r, g, b):
    b = not ((((r >= 70 and r <= 160) and (g >= 95 and g <= 200) and (b > 115)) or (r < 70 or g < 70 or b < 70)) and not (r>=115 and r<=160 and g>=140 and g<=196 and b>=115 and b<=170))
    # print(b)
    return b

class NumberOfIslands:
    def __init__(self, graph, is_land=None, out_folder='data'):
        # TODO: check grid
        self.graph = graph
        self.height = graph[0].shape[0]
        self.width = graph[0].shape[1]
        self.visited = np.zeros(rs.shape)

        self.neighbors_rook = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # N, E, S, W
        self.neighbors_queen = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (-1, 1), (0, -1), (-1, -1)]  # N, NE, E, SE, S, SW, W, NW
        self.contiguity = self.neighbors_rook

        self.out_folder = out_folder
        self.colors = {
            'current': [205, 0, 0],
            'land': [75, 150, 0],
        }
        self.previous_color = [0, 0, 0]
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
        rs, gs, bs = self.graph

        options = {
            'driver': 'GTiff', 'dtype': 'uint8', 'nodata': None, 'width': self.width, 'height': self.height, 'count': 3, 'crs': None, 'tiled': False, 'interleave': 'pixel', 'compress': 'lzw'
        }

        with rasterio.open(f'{self.out_folder}/noi_{self.print_index}.tif', 'w' , **options) as dst:
            dst.write(rs.astype(rasterio.uint8), 1)
            dst.write(gs.astype(rasterio.uint8), 2)
            dst.write(bs.astype(rasterio.uint8), 3)

        self.print_index += 1


    def is_valid(self, row, col):
        return (row >= 0) and (row < self.height) and (col >= 0) and (col < self.width)

    def dfs(self, row, col):
        rs, gs, bs = self.graph

        # land
        r, g, b = self.colors['land']
        rs[row][col] = r
        bs[row][col] = g
        gs[row][col] = b
        self.visited[row][col] = 1

        self.write_raster()

        for n in self.contiguity:
            n_r = row + n[0]
            n_c = col + n[1]

            # Case: land
            # if self.is_valid(n_r, n_c) and self.grid[n_r][n_c] == 1:
            if self.is_valid(n_r, n_c) and self.is_land(rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]) and not self.visited[n_r][n_c]:
                self.dfs(n_r, n_c)

            # Case: water (near land)
            # elif self.is_valid(n_r, n_c) and self.grid[n_r][n_c] == 0:
            #     self.grid[n_r][n_c] = ' '

    def bfs(self, r, c):
        return 0

    def number_of_islands(self, algorithm="dfs", contiguity="rook"):
        algorithm = {"dfs": self.dfs, "bfs": self.bfs}[algorithm]
        self.contiguity = {"rook": self.neighbors_rook, "queen": self.neighbors_queen}[contiguity]

        # if not self.grid or not self.grid[0]:
        #     return 0
            
        row = self.height
        col = self.width
        count = 0

        rs, gs, bs = self.graph
        self.visited = np.zeros(rs.shape)
        
        for i in range(0, row):
            for j in range(0, col):

                # print(f"{i}, {j}")

                # Case: Land
                # if self.grid[i][j] == 1:
                if self.is_land(rs[i][j], gs[i][j], bs[i][j]) and not self.visited[i][j]:
                    algorithm(i, j)
                    count += 1
                    

                # Case: Water (not near land) (OPTIONAL)
                # elif self.grid[i][j] == 0:
                #     self.grid[i][j] = ' '

                # print_grid(graph)
            
        return count

import os
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'data')

noi = NumberOfIslands([rs, gs, bs], is_land=is_land, out_folder=filename)
print(noi.number_of_islands())

# for i in range(bs.shape[0]):
#     for j in range(bs.shape[1]):
#         r = rs[i][j]
#         g = gs[i][j]
#         b = bs[i][j]

#         if is_land(i, j):
#             rs[i][j] = 255
#             gs[i][j] = 255
#             bs[i][j] = 255


