import os
import sys
import time

import rasterio
import numpy as np
import random

class NumberOfIslands:
    def __init__(self, graph, algorithm="dfs", contiguity="rook", is_land=None, out=False, out_folder='data'):
        sys.setrecursionlimit(100000)

        self.graph = graph  # grid is a list of 3 numpy arrays pertaining to 3 bands (i.e. r, g, b)
        self.height = graph[0].shape[0]
        self.width = graph[0].shape[1]
        self.visited = np.zeros(self.graph[0].shape) # keep record of visitations in memory -> no double-visiting
        self.queue = [] # used for bfs

        self.neighbors_rook = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # N, E, S, W
        self.neighbors_queen = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (-1, 1), (0, -1), (-1, -1)]  # N, NE, E, SE, S, SW, W, NW
        
        self.algorithm = {"dfs": self.dfs, "bfs": self.bfs}[algorithm]
        self.contiguity = {"rook": self.neighbors_rook, "queen": self.neighbors_queen}[contiguity]

        self.out = out
        self.out_folder = out_folder
        self.out_options = {
            'driver': 'GTiff', # TODO: smaller file type?
            'dtype': 'uint8', 
            'nodata': None, 
            'width': self.width if (self.width % 2) == 0 else self.width-1,     # must be even
            'height': self.height if (self.height % 2) == 0 else self.height-1, # must be even
            'count': 3, # 3 bands (i.e. rgb)
            'crs': None, 
            'tiled': False, 
            'interleave': 'pixel', 
            'compress': 'lzw'
        }

        # cursor shape (+) around cell being visited for visualizations. 
        # does not necessarily reflect a cell's neighbors, just used for increased visibility
        self.cursor = [
            (-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0),   # N
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),         # E
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),         # S
            (0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6),   # W
        ]

        self.colors = {
            'cursor':  [205, 0, 0],
            # 'land':     [50, 250, 50],
            'shore':     [250, 100, 50],
        }
        self.previous_color = [0, 0, 0]
        self.cursor_previous_colors = [[0, 0, 0] for i in range(len(self.cursor))]
        self.print_index = 0

        # register a simple classification function of type ((r, g, b) -> boolean)
        if is_land is None:
            # this is terrible and should never be used
            self.is_land = lambda r, g, b : r + g + b > 300 
        else:
            # thats more like it
            self.is_land = is_land

    def write_raster(self):
        """
        write the state of the search grid to a new raster for visualization

        args:
        effects: produces a new raster
        returns: 
        """

        rs, gs, bs = self.graph

        # write all 3 bands to a new raster
        with rasterio.open(f'{self.out_folder}/noi_{self.print_index:06}.tif', 'w' , **self.out_options) as dst:
            dst.write(rs.astype(rasterio.uint8), 1)
            dst.write(gs.astype(rasterio.uint8), 2)
            dst.write(bs.astype(rasterio.uint8), 3)

        # increment the number of rasters produced
        self.print_index += 1

    def color_cursor(self, row, col):
        """
        color the cell being visited and the nearby cells for visibility

        args: (row, col), the location of the cell being visited
        effects: colors current cell and nearby cells, resets colors of cells previously colored by cursor
        returns: 
        """

        rs, gs, bs = self.graph

        # save current color
        self.previous_color = [rs[row][col], gs[row][col], bs[row][col]]

        # color current cell
        r, g, b = self.colors['cursor']
        rs[row][col] = r
        gs[row][col] = g
        bs[row][col] = b

        # color the cursor (cell being visited & cardinal directions for visibility)
        for k, n in enumerate(self.cursor):
            n_r = row + n[0]
            n_c = col + n[1]
            if self.is_valid(n_r, n_c):
                self.cursor_previous_colors[k] = [rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]]
                rs[n_r][n_c] = r
                gs[n_r][n_c] = g
                bs[n_r][n_c] = b

        self.write_raster()

        # reset cell's color
        r, g, b = self.previous_color
        rs[row][col] = r
        gs[row][col] = g
        bs[row][col] = b

        # reset cursor's colors
        for k, n in enumerate(self.cursor):
            n_r = row + n[0]
            n_c = col + n[1]

            if self.is_valid(n_r, n_c):
                r, g, b = self.cursor_previous_colors[k]
                rs[n_r][n_c] = r
                gs[n_r][n_c] = g
                bs[n_r][n_c] = b

    def is_valid(self, row, col):
        """
        ensure location is within the raster's bounds

        args: (row, col), the location of the cell being visited
        effects: 
        returns: 
        """
        # ensure location is within the raster's bounds
        return (row >= 0) and (row < self.height) and (col >= 0) and (col < self.width)

    def dfs(self, row, col):
        """
        Depth First Search
        see: https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/

        note: due to python's recursion limitations, this will fail on large rasters
        args: (row, col), the location of the cell being visited
        effects: write state of search to a new raster if self.out is set
        returns: 
        """

        rs, gs, bs = self.graph

        # mark cell as visited
        self.visited[row][col] = 1

        # if visualizing, skip some cells to save memory
        if self.out and (col % 4 == 0):
            self.color_cursor(row, col)

        for i, n in enumerate(self.contiguity):
            n_r = row + n[0]
            n_c = col + n[1]

            if self.is_valid(n_r, n_c) and not self.visited[n_r][n_c]:
                # Case: land
                if self.is_land(rs[n_r][n_c], gs[n_r][n_c], bs[n_r][n_c]):
                    self.dfs(n_r, n_c)

                # Case: shore (water near land)
                else:
                    r, g, b = self.colors['shore']
                    rs[n_r][n_c] = r
                    gs[n_r][n_c] = g
                    bs[n_r][n_c] = b

    def bfs(self, row, col):
        """
        Breadth First Search
        see: https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/

        args: (row, col), the location of the cell being visited
        effects: write state of search to a new raster if self.out is set
        returns: 
        """
        rs, gs, bs = self.graph

        # mark cell as visited
        self.visited[row][col] = 1
        self.queue.append([row, col])

        while self.queue:
            s = self.queue.pop(0)

            # if visualizing, skip some cells to save memory
            if self.out and (s[1] % 4 == 0):
                self.color_cursor(s[0], s[1])

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

                    # Case: shore (water near land)
                    else:
                        r, g, b = self.colors['shore']
                        rs[n_r][n_c] = r
                        gs[n_r][n_c] = g
                        bs[n_r][n_c] = b

    def number_of_islands(self):
        """
        traverse raster, trigger bfs or dfs when land is hit

        args: 
        effects: write state of search to a new raster if self.out is set
        returns: count (number of islands in input raster)
        """


        # if input raster has incorrect shape do nothing
        if not self.graph or not self.width or not self.height:
            return 0
            
        row = self.height
        col = self.width
        count = 0

        rs, gs, bs = self.graph
        self.visited = np.zeros(rs.shape)   # re-init visited
        
        for i in range(0, row):
            for j in range(0, col):

                # if visualizing, skip some cells to save memory
                if self.out and not self.visited[i][j] and (j % 20 == 0):
                    self.color_cursor(i, j)

                # Case: Land
                if self.is_land(rs[i][j], gs[i][j], bs[i][j]) and not self.visited[i][j]:
                    self.algorithm(i, j)
                    count += 1

                # Case: Water (not near land) (OPTIONAL)
                # elif self.grid[i][j] == 0:
                #     self.grid[i][j] = ' '
            
        return count