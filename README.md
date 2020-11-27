# Number of Islands

This tool runs analyzes geospatial raster imagery to identify the number and location of distinct islands. The grid is iteratively traversed pixel by pixel until land is hit, triggering one of the search algorithms to 'visit' the contiguous land before returning to the search.

[Visualization of the DFS and BFS variants](https://youtu.be/kEoZuNdHLas)

Analysis performed on Blue Marble dataset, courtesy of NASA. Written in Python with NumPy and Rasterio and compiled with ffmpeg.
