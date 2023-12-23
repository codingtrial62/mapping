
import folium
from flask import Flask, render_template
import os
import pandas as pd
import geopandas
from folium.plugins import FastMarkerCluster
from pathlib import Path
from sqlalchemy import create_engine
import shapely as shp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
# secret_key = os.environ.get('SECRET_KEY')
# app = Flask(__name__)
# app.config['SECRET_KEY'] = secret_key


path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_to_enr = '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml'
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))
#
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ltac_obstacles.db'
# db = SQLAlchemy()
# db.init_app(app)
def read_area_3_4_db(path_list, area: int, path_list_xml):
    """
    This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
    LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
    WGS84. Also caution for file paths especially having space in it. Sometimes manually changing file names may be better:).

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


def read_area2a():
    path_list = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
    for i in path_list:
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area2a_obstacles.db', echo=False)
        layer_name = str(i)[61:].replace('/', '_').replace('.gdb', '').lower()
        if path_list.index(i) == 0:
            gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
        else:
            bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
            gdf = pd.concat([gdf, bdf], ignore_index=True)

    return gdf


def read_enr_obs_db(db_path):
    gdf = geopandas.read_file(db_path)
    return gdf


def chunks(xs, n):
    """
    This function splits a list into n sized chunks. Thanks to answer from
    https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    To properly create LineStrings, MultiLineStrings and Polygons we need to split the coordinates into chunks of 2.
    """
    n = max(1, n)
    return [tuple(xs[i:i + n]) for i in range(0, len(xs), n)]


def chunks2(xs, n):
    """
    This function is a different implementation to suit our data to get coordinates as lists which has
     two coordinates each.
    :param xs:
    :param n:
    :return:
    """
    n = max(1, n)
    coordinate_list = []
    for i in range(0, len(xs), n):
        coordinate_list.append(xs[i:i + n])
    for t in coordinate_list:
        ind = coordinate_list.index(t)
        coordinate_list[ind] = [float(t[0]), float(t[1])]
    return coordinate_list
def read_ltac_area3():
    engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=True)

    point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)

    for i in range(point_df.shape[0]):
        point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
                                                float(point_df.loc[i, 'Coordinate'].split(' ')[1]))



    line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
    for i in range(line_df.shape[0]):
        line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))



    polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)
    for i in range(polygon_df.shape[0]):

        if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
            polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
            polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
        else:
            polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))
    ltac_all = pd.concat([point_df,line_df, polygon_df], ignore_index=True)
    return ltac_all


def read_ad_obs(path_to_ad):
    layer_name = str(path_list_ad[1])[64:78].lower()
    engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db', echo=False)
    gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
    for p in path_list_ad[1:]:
        layer_name = str(p)[64:78].lower()
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db', echo=False)
        gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
        if path_list_ad.index(p) == 1:
            pass
        else:
            cdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
            gdf = pd.concat([gdf, cdf], ignore_index=True)


    return gdf

#ad_df = read_ad_obs(path_list_ad)
# read_area2a()
# read_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
# read_area_3_4_db(path_list_area_4, 4, path_list_area_4_xml)
# read_ltac_area3()
# read_enr_obs_db(path_to_enr)

print(path_list_ad)





