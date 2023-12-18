import folium
from flask import Flask, request, render_template_string, render_template, redirect
import matplotlib.pyplot as plt
import pandas as pd
import geopandas
import lxml
from flask_sqlalchemy import SQLAlchemy
from folium import Popup
from folium.plugins import MarkerCluster
from geoalchemy2 import Geometry, Geography, Raster, RasterElement, WKBElement, CompositeElement, WKTElement
from sqlalchemy.orm import relationship
import rasterio
from rasterio.plot import show
import pyogrio
import numpy as np
from pathlib import Path
import sqlite3 as sq
from sqlalchemy import MetaData, create_engine, DateTime, Column, Integer, String, Float, Boolean, ForeignKey, Table, \
    func, select, BLOB
import shapely as shp

ad_list = ['LTAC', 'LTAF', 'LTAI', 'LTAJ', 'LTAN', 'LTAP', 'LTAR', 'LTAS', 'LTAT', 'LTAU', 'LTAW', 'LTAY', 'LTAZ',
           'LTBA', 'LTBD', 'LTBF', 'LTBH', 'LTBJ', 'LTBO', 'LTBQ', 'LTBR', 'LTBS', 'LTBU', 'LTBY', 'LTBZ', 'LTCA',
           'LTCB', 'LTCC', 'LTCD', 'LTCE', 'LTCF', 'LTCG', 'LTCI', 'LTCJ', 'LTCK', 'LTCL', 'LTCM', 'LTCN', 'LTCO',
           'LTCP', 'LTCR', 'LTCS', 'LTCT', 'LTCU', 'LTCV', 'LTCW', 'LTDA', 'LTFB', 'LTFC', 'LTFD', 'LTFE', 'LTFG',
           'LTFH', 'LTFJ', 'LTFK', 'LTFM', 'LTFO', ]
mdb_path = '/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles/LTAC_AREA_3/AREA3.mdb'
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'fea4877a6edb053d1acc1f7841d78dca98f2d5bab0af7220522cf94ef685bc2d'
path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))

engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=True)

def chunks(xs, n):
    n = max(1, n)
    return [xs[i:i + n] for i in range(0, len(xs), n)]

def chunks2(xs, n):
    n = max(1, n)
    coordinate_list = []
    for i in range(0, len(xs), n):
        coordinate_list.append(xs[i:i + n])
    for t in coordinate_list:
        ind = coordinate_list.index(t)
        coordinate_list[ind] = [float(t[0]), float(t[1])]
    return coordinate_list
        #return tuple(xs[i:i + n])

def read_area_3_4_db(path_list, area: int, path_list_xml):
    """
    This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
    LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
    WGS84. Also caution for file paths especially having space in it.

    """
    if area == 3:
        for i in path_list:
            layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
            engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area3_obstacles.db', echo=False)
            if path_list.index(i) == 0:
                gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
            else:
                bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
                gdf = pd.concat([gdf, bdf], ignore_index=True)

    elif area == 4:
        for j in path_list:
            layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
            engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
            if path_list.index(j) == 0:
                gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
            else:
                bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
                gdf = pd.concat([gdf, bdf], ignore_index=True)

        for k in path_list_xml:
            layer_name = str(k)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
            engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
            if path_list_xml.index(k) == 0:
                xdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
            else:
                ydf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
                xdf = pd.concat([xdf, ydf], ignore_index=True)
        gdf = pd.concat([gdf, xdf], ignore_index=True)
    else:
        print('Wrong area number. Please enter 3 or 4.')
    return gdf


#ggdf = read_area_3_4_db(path_list_area_4,4 , path_list_area_4_xml)
for n in path_list_area_2:
    engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
    layer_name = str(n)[69:].replace('/', '_').replace('.gdb', '').lower()
    bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
    coords = bdf.get_coordinates(ignore_index=True)
    for o in range(bdf.shape[0]):
        if bdf.loc[o, 'GEOMETRY'].geom_type == 'Point':
            print(f"{o} {layer_name} Point coordinates: {coords.loc[o,'y']}N {coords.loc[o,'x']}E")

        elif bdf.loc[o,'GEOMETRY'].geom_type == 'MultiLineString':
            print(f"{o} {layer_name} MultiLineString coordinates: {chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '),2)}")
#print(ggdf.groupby(ggdf.geometry.type).count())