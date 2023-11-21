import dted
import numpy as np
from pathlib import Path
from dted import *
import matplotlib.pyplot as plt



dted_file = Path("/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTAC_AREA_4/R1_AREA_4_03L/Terrain/DTED/DTED2/E032/N40.DT2")
tile = Tile(dted_file)
print(plt.imshow(tile.data.T[::-1], cmap="hot"))