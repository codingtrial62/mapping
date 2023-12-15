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
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))

