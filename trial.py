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

#
# if 'BUILDING' in df.loc[i, 'name'] or 'BULDING' in df.loc[i, 'name']:
#     # kw = {"prefix": "fa", "color": "green", "icon": "building"}
#     # icons = folium.Icon(**kw)
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/building.png')
#
#
# elif 'MAST' in df.loc[i, 'name']:
#     if df.loc[i, 'name'] == 'LIGHTING MAST':
#         # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
#         # icons = folium.Icon(**kw)
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/street-light.png')
#
#     elif df.loc[i, 'name'] == 'APRON LIGHTING MAST' or df.loc[i, 'name'] == 'APRON LIGTHING MAST':
#         # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
#         # icons = folium.Icon(**kw)
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/apron_lighting.png')
#
#     else:
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/mast.png')
#         # folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/aixm_mapping/icons8-pylon-64.png')
#
#
#
# elif df.loc[i, 'name'] == 'MOSQUE' or df.loc[i, 'name'] == 'MOSQUE_DOME':
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/mosque.png')
#
#
# elif df.loc[i, 'name'] == 'MINARET':
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/minaret.png')
#
# elif 'SURVEILLANCE TOWER' in df.loc[i, 'name'] or 'TWR' in df.loc[i, 'name']:
#     kw = {"prefix": "fa", "color": "pink", "icon": "tower-observation"}
#     icons = folium.Icon(**kw)
#
# elif 'ANTENNA' in df.loc[i, 'name']:
#     if df.loc[i, 'name'] == 'GSM ANTENNA':
#         # kw = {"prefix": "fa", "color": "purple", "icon": "signal"}
#         # icons = folium.Icon(**kw)
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gsm_anten.png')
#
#     elif df.loc[i, 'name'] == 'DME ANTENNA' or df.loc[i, 'name'] == 'DME ANTENNA(GP)':
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/dme_antenna.png')
#
#     elif df.loc[i, 'name'] == 'GLIDE PATH  ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA' \
#             or df.loc[i, 'name'] == 'GP ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA':
#         icons = folium.CustomIcon(
#             icon_image='/Users/dersim/PycharmProjects/mapping/icons/glidepath_antenna.png')
#
#     elif df.loc[i, 'name'] == 'LLZ ANTENNA':
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/llz_ant.png')
#
#     elif df.loc[i, 'name'] == 'NDB ANTENNA':
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/ndb_antenna.png')
#
#     elif df.loc[i, 'name'] == 'TACAN ANTENNA':
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tacan_antenna.png')
#
#     elif df.loc[i, 'name'] == 'VOR ANTENNA':
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor_antenna.png')
#
#     elif df.loc[i, 'name'] == 'NF ANTENNA':
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/nf_antenna.png')
#
#     else:
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/antenna.png')
#
# elif df.loc[i, 'name'] == 'CHIMNEY' or df.loc[i, 'name'] == 'SHAFT':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/chimney.png')
#
# elif df.loc[i, 'name'] == 'ANM' or 'ANEMO' in df.loc[i, 'name']:
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/anemometer.png')
#
#
# elif 'WIND' in df.loc[i, 'name']:
#     if 'DIRECTION' in df.loc[i, 'name']:
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-direction.png')
#
#     elif 'ROSE' in df.loc[i, 'name']:
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-rose.png')
#
#
#     elif 'TURBINE' in df.loc[i, 'name'] or 'T' in df.loc[i, 'name']:
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-turbine.png')
#
#
#     else:
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/windsock.png')
#
#
# elif 'WDI' in df.loc[i, 'name']:
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-direction.png')
#
# elif 'APPROACH' in df.loc[i, 'name']:
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/landing-track.png')
#
# elif 'POLE' in df.loc[i, 'name']:
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/pole.png')
#
#
# elif df.loc[i, 'name'] == 'LIGHTNING ROD' or df.loc[i, 'name'] == 'PARATONER' or df.loc[
#     i, 'name'] == 'PARATONNERRE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/lightning-rod.png')
#
#
# elif df.loc[i, 'name'] == 'HOSPITAL':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/hospital.png')
#
#
# elif df.loc[i, 'name'] == 'DME' or df.loc[i, 'name'] == 'DME ILS/GP':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/dme.png')
#
#
# elif df.loc[i, 'name'] == 'NDB':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/ndb.png')
#
#
# elif df.loc[i, 'name'] == 'TACAN' or df.loc[i, 'name'] == 'TACAN CONTAINER':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tacan.png')
#
#
# elif df.loc[i, 'name'] == 'VOR' or df.loc[i, 'name'] == 'VOR CONTAINER' or df.loc[i, 'name'] == 'VOR STATION':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor.png')
#
#
# elif df.loc[i, 'name'] == 'VOR+DME' or df.loc[i, 'name'] == 'VOR/DME':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor_dme.png')
#
#
# elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/nf_antenna.png')
#
#
# elif 'LIGHT' in df.loc[i, 'name']:
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/street-light.png')
#
#
# elif df.loc[i, 'name'] == 'GREENHOUSE' or df.loc[i, 'name'] == 'GREEN HOUSE' or df.loc[
#     i, 'name'] == 'PLANT-HOUSE' or df.loc[i, 'name'] == 'GARDEN FRAME':
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/greenhouse.png')
#
# elif df.loc[i, 'name'] == 'SILO' or df.loc[i, 'name'] == 'GRAIN SILO':
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/silo.png')
#
#
# elif df.loc[i, 'name'] == 'STADIUM':
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/stadium.png')
#
#
# elif 'HOOK BARRIER' in df.loc[i, 'name']:
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/hook.png')
#
#
# elif 'NET BARRIER' in df.loc[i, 'name']:
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/net.png')
#
#
# elif df.loc[i, 'name'] == 'CONCRETE BARRIER' or df.loc[i, 'name'] == 'CONCRETE BLOCK' or df.loc[
#     i, 'name'] == 'BETON BARIYER':
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/concrete_barrier.png')
#
#
# elif 'WALL' in df.loc[i, 'name']:
#
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wall.png')
#
#
# elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/nf_antenna.png')
#
#
# elif (df.loc[i, 'name'] == 'DVOR' or df.loc[i, 'name'] == 'DVOR_LC' or df.loc[i, 'name'] == 'DVOR_MONITOR'
#       or df.loc[i, 'name'] == 'FFM_18' or df.loc[i, 'name'] == 'FFM_17L' or df.loc[i, 'name'] == 'FFM-35R'
#       or df.loc[i, 'name'] == "FFM_34L" or df.loc[i, 'name'] == 'FFM_36' or df.loc[i, 'name'] == 'GLIDE PATH'
#       or df.loc[i, 'name'] == 'GLIDEPAT CON.' or df.loc[i, 'name'] == 'GLIDE PATH SHELTER' or df.loc[
#           i, 'name'] == 'GLIDE PATH CONTAINER'
#       or df.loc[i, 'name'] == 'GP' or df.loc[i, 'name'] == 'GP CABIN' or df.loc[i, 'name'] == 'GP STATION'
#       or df.loc[i, 'name'] == 'GP_16R_MONITOR' or df.loc[i, 'name'] == 'GP/NAVAID' or df.loc[
#           i, 'name'] == 'GP/DME'
#       or df.loc[i, 'name'] == 'GP_16R_OBS_LT' or df.loc[i, 'name'] == 'GP_17L_MONITOR' or df.loc[
#           i, 'name'] == 'GP_17L_OBS_LT'
#       or df.loc[i, 'name'] == 'GP_34L_MONITOR' or df.loc[i, 'name'] == 'GP_18_OBS_LT' or df.loc[
#           i, 'name'] == 'GP_18_MONITOR'
#       or df.loc[i, 'name'] == 'GP_34L_OBS_LT' or df.loc[i, 'name'] == 'GP_35R_MONITOR' or df.loc[
#           i, 'name'] == 'GP_35R_OBS_LT'
#       or df.loc[i, 'name'] == 'LLZ CON.' or df.loc[i, 'name'] == 'GP_36_OBS_LT' or df.loc[
#           i, 'name'] == 'GP_36_MONITOR'
#       or df.loc[i, 'name'] == 'LLZ CONTAINER' or df.loc[i, 'name'] == 'LLZ16' or df.loc[i, 'name'] == 'LLZ_18'
#       or df.loc[i, 'name'] == 'RVR' or df.loc[i, 'name'] == 'PAPI_COVER' or df.loc[i, 'name'] == 'LOCALIZER' or
#       df.loc[i, 'name'] == 'RAPCON'
#       or df.loc[i, 'name'] == 'RVR-SENSOR') or df.loc[i, 'name'] == 'NDB FIELD' or df.loc[i, 'name'] == 'GCA' or \
#         df.loc[i, 'name'] == 'SENTRY BOX' \
#         or df.loc[i, 'name'] == 'NFM_34L':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/other_navigation_aid.png')
#
# elif df.loc[i, 'name'] == 'GSM BASE STATION' or df.loc[i, 'name'] == 'GSM STATION':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gsm_anten.png')
#
#
# elif df.loc[i, 'name'] == 'GAS STATION':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gas-station.png')
#
#
# elif df.loc[i, 'name'] == 'RADAR_STATION':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/radar.png')
#
#
# elif (df.loc[i, 'name'] == 'CABIN' or df.loc[i, 'name'] == 'CONSTRUCTION' or df.loc[i, 'name'] == 'COTTAGE'
#       or df.loc[i, 'name'] == 'GUARD COTTAGE' or df.loc[i, 'name'] == 'STRUCTURE'):
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/cabin.png')
#
#
# elif df.loc[i, 'name'] == 'HANGAR':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/hangar.png')
#
#
# elif df.loc[i, 'name'] == 'MILITARY TRENCH':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/trench.png')
#
#
# elif df.loc[i, 'name'] == 'REFLECTOR':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/reflector.png')
#
#
# elif df.loc[i, 'name'] == 'ROCK' or df.loc[i, 'name'] == 'STACK' \
#         or df.loc[i, 'name'] == 'CLIFF':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/rock_stack_cliff.png')
#
#
# elif df.loc[i, 'name'] == 'TREE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tree.png')
#
#
# elif df.loc[i, 'name'] == 'VAN CASTLE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/castle.png')
#
#
# elif df.loc[i, 'name'] == 'BRIDGE_DECK':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/bridge_deck.png')
#
#
# elif df.loc[i, 'name'] == 'TRANSFORMER':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/transformer.png')
#
#
# elif df.loc[i, 'name'] == 'TRAFFIC_SIGN' or df.loc[i, 'name'] == 'TRAFFIC BOARD' \
#         or df.loc[i, 'name'] == 'SIGNBOARD':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/sign_board.png')
#
#
# elif df.loc[i, 'name'] == 'PYLON':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/pylon.png')
#
#
# elif df.loc[i, 'name'] == 'CRANE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/crane.png')
#
#
# elif df.loc[i, 'name'] == 'ARFF POOL':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/arff_pool.png')
#
#
# elif df.loc[i, 'name'] == 'ENERGY TRANSMISSION LINE' or df.loc[i, 'name'] == 'POWER_TRANSMISSION_LINE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/transmission.png')
#
# elif df.loc[i, 'name'] == 'CONTAINER':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/container.png')
#
#
# elif 'TERRAIN' in df.loc[i, 'name']:
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/terrain.png')
#
#
# elif df.loc[i, 'name'] == 'BASE STATION':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/base_station.png')
#
#
# elif df.loc[i, 'name'] == 'BILLBOARD':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/billboard.png')
#
#
# elif df.loc[i, 'name'] == 'CAMERA PANEL':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/panel.png')
#
#
# elif df.loc[i, 'name'] == 'FENCE' or df.loc[i, 'name'] == 'WIRE FENCE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/fence.png')
#
#
# elif df.loc[i, 'name'] == 'FUEL_TANK':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/fuel_tank.png')
#
#
# elif df.loc[i, 'name'] == 'WATER TANK':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/water_tank.png')
#
#
# elif df.loc[i, 'name'] == 'WATER ROSERVOIR':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/reservoir.png')
#
#
# elif df.loc[i, 'name'] == 'ENERGY CABIN':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/energy_cabin.png')
#
#
# elif df.loc[i, 'name'] == 'METEOROLOGY DEVICE':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/meteo_device.png')
#
#
# elif df.loc[i, 'name'] == 'OKIS':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/okis.png')
#
#
# elif df.loc[i, 'name'] == 'TERMINAL':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/terminal.png')
#
#
# elif df.loc[i, 'name'] == 'VOICE BIRD SCARING SYSTEM':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vbss.png')
#
#
# elif df.loc[i, 'name'] == 'WATCH BOX':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/watch_box.png')
#
#
# elif df.loc[i, 'name'] == 'GNSS_MEASUREMENT_POINT':
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gnss.png')
#
#
#
# else:
#     icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/laughing.png')