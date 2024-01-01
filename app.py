import os
from pathlib import Path

import folium
import geopandas
import pandas as pd
from shapely import wkt
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from folium.plugins import FastMarkerCluster, FeatureGroupSubGroup, MarkerCluster
from sqlalchemy import create_engine
import gunicorn
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5

from flask_caching import Cache

cache = Cache()
'''
ltfh_area2 and 4 coordinates column manually changed to coordinate on dbviewer.
792-35-A1-R1-40-5047.   Coordinates end with 38* manually changed on dbviewer. 
'''

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev_key',
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://') or \
                            'sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# app.config.from_mapping(
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key',
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
#                               'sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'),
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
# )
db = SQLAlchemy()
migrate = Migrate()
db.init_app(app)
migrate.init_app(app, db)

path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_to_enr = '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml'
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))


class AerodromeObstacles(db.Model):
    __tablename__ = 'ad_obstacles'
    id = db.Column(db.Integer, primary_key=True)
    aerodrome = db.Column(db.String())
    coordinate = db.Column(db.String())
    gml_id = db.Column(db.String())
    identifier = db.Column(db.String())
    beginposition = db.Column(db.String())
    interpretation = db.Column(db.String())
    sequencenumber = db.Column(db.Integer)
    correctionnumber = db.Column(db.Integer)
    timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
    name = db.Column(db.String())
    type = db.Column(db.String())
    lighted = db.Column(db.String())
    group = db.Column(db.String())
    verticalextent = db.Column(db.Float)
    verticalextent_uom = db.Column(db.String())
    timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
    designator = db.Column(db.String())
    elevation = db.Column(db.Float)
    elevation_uom = db.Column(db.String())
    colour = db.Column(db.String(), nullable=True)
    geo = db.Column(db.String())


class EnrouteObstacles(db.Model):
    __tablename__ = "enr_obstacles"
    id = db.Column(db.Integer, primary_key=True)
    coordinate = db.Column(db.String())
    gml_id = db.Column(db.String())
    identifier = db.Column(db.String())
    beginposition = db.Column(db.String())
    interpretation = db.Column(db.String())
    sequencenumber = db.Column(db.Integer)
    correctionnumber = db.Column(db.Integer)
    timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
    name = db.Column(db.String())
    type = db.Column(db.String())
    lighted = db.Column(db.String())
    group = db.Column(db.String())
    verticalextent = db.Column(db.Integer)
    verticalextent_uom = db.Column(db.String())
    timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
    designator = db.Column(db.String())
    elevation = db.Column(db.Integer)
    elevation_uom = db.Column(db.String())
    colour = db.Column(db.String())
    geo = db.Column(db.String())


class Area2aObstacles(db.Model):
    __tablename__ = "area2a_obstacles"
    id = db.Column(db.Integer, primary_key=True)
    aerodrome = db.Column(db.String())
    obstacle_identifier = db.Column(db.String())
    horizontal_accuracy = db.Column(db.Float)
    horizontal_confidence_level = db.Column(db.Integer)
    elevation = db.Column(db.Float)
    height = db.Column(db.Float)
    vertical_accuracy = db.Column(db.Float)
    vertical_confidence_level = db.Column(db.Integer)
    obstacle_type = db.Column(db.String())
    integrity = db.Column(db.String())
    date_and_time_stamp = db.Column(db.String())
    operations = db.Column(db.String())
    effectivity = db.Column(db.String())
    lighting = db.Column(db.String())
    marking = db.Column(db.String())
    horizontal_extent = db.Column(db.String())
    obstacle_name = db.Column(db.String())
    marking_details = db.Column(db.String())
    lighting_color = db.Column(db.String())
    coordinate = db.Column(db.String())
    shape_length = db.Column(db.Float)
    geo = db.Column(db.String())


class Area3Obstacles(db.Model):
    __tablename__ = "area3_obstacles"
    id = db.Column(db.Integer, primary_key=True)
    aerodrome = db.Column(db.String())
    obstacle_identifier = db.Column(db.String())
    horizontal_accuracy = db.Column(db.Float)
    horizontal_confidence_level = db.Column(db.Integer)
    elevation = db.Column(db.Float)
    height = db.Column(db.Float)
    vertical_accuracy = db.Column(db.Float)
    vertical_confidence_level = db.Column(db.Integer)
    obstacle_type = db.Column(db.String())
    integrity = db.Column(db.String())
    date_and_time_stamp = db.Column(db.String())
    operations = db.Column(db.String())
    effectivity = db.Column(db.String())
    lighting = db.Column(db.String())
    marking = db.Column(db.String())
    obstacle_name = db.Column(db.String())
    lighting_color = db.Column(db.String())
    marking_details = db.Column(db.String())
    coordinate = db.Column(db.String())
    horizontal_extent = db.Column(db.String())
    shape_length = db.Column(db.Float)
    geo = db.Column(db.String())


class LtacArea3Obstacles(db.Model):
    __tablename__ = "ltac_area3_obstacles"
    id = db.Column(db.Integer, primary_key=True)
    Obstacle_Identifier = db.Column(db.String())
    Horizontal_Accuracy = db.Column(db.Float)
    Horizontal_Confidence_Level = db.Column(db.Integer)
    Elevation = db.Column(db.Float)
    Height = db.Column(db.Float)
    Vertical_Accuracy = db.Column(db.Float)
    Vertical_Confidence_Level = db.Column(db.Integer)
    Obstacle_Type = db.Column(db.String())
    Integrity = db.Column(db.String())
    Date_And_Time_Stamp = db.Column(db.String())
    Operations = db.Column(db.String())
    Effectivity = db.Column(db.String())
    Lighting = db.Column(db.String())
    Marking = db.Column(db.String())
    Obstacle_Name = db.Column(db.String())
    Lighting_Color = db.Column(db.String())
    Marking_Details = db.Column(db.String())
    Coordinate = db.Column(db.String())
    SHAPE_Length = db.Column(db.Float)
    SHAPE_Area = db.Column(db.String())
    Horizontal_Extent = db.Column(db.String())
    geo = db.Column(db.String())


class Area4Obstacles(db.Model):
    __tablename__ = "area4_obstacles"
    id = db.Column(db.Integer, primary_key=True)
    aerodrome = db.Column(db.String())
    obstacle_identifier = db.Column(db.String())
    horizontal_accuracy = db.Column(db.Float)
    horizontal_confidence_level = db.Column(db.Integer)
    elevation = db.Column(db.Float)
    height = db.Column(db.Float)
    vertical_accuracy = db.Column(db.Float)
    vertical_confidence_level = db.Column(db.Integer)
    obstacle_type = db.Column(db.String())
    integrity = db.Column(db.String())
    date_and_time_stamp = db.Column(db.String())
    operations = db.Column(db.String())
    effectivity = db.Column(db.String())
    lighting = db.Column(db.String())
    marking = db.Column(db.String())
    horizontal_extent = db.Column(db.String())
    obstacle_name = db.Column(db.String())
    marking_details = db.Column(db.String())
    lighting_color = db.Column(db.String())
    coordinate = db.Column(db.String())
    shape_length = db.Column(db.Float)
    shape_area = db.Column(db.String())
    geo = db.Column(db.String())


class LtfmArea4Obstacles(db.Model):
    __tablename__ = "ltfm_area4_obstacles"
    id = db.Column(db.Integer, primary_key=True)
    coordinate = db.Column(db.String())
    gml_id = db.Column(db.String())
    identifier = db.Column(db.String())
    beginposition = db.Column(db.String())
    interpretation = db.Column(db.String())
    sequencenumber = db.Column(db.Float)
    correctionnumber = db.Column(db.Float)
    timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
    name = db.Column(db.String())
    type = db.Column(db.String())
    lighted = db.Column(db.String())
    group = db.Column(db.String())
    verticalextent = db.Column(db.Float)
    verticalextent_uom = db.Column(db.String())
    timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
    designator = db.Column(db.Float)
    elevation = db.Column(db.Float)
    elevation_uom = db.Column(db.String())
    colour = db.Column(db.String())
    geo = db.Column(db.String())


with app.app_context():
    db.create_all()



cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    # Fall back to simple in memory cache (development)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app,
                   config={'CACHE_TYPE': 'SASLMemcachedCache',
                           'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                           'CACHE_MEMCACHED_USERNAME': cache_user,
                           'CACHE_MEMCACHED_PASSWORD': cache_pass,
                           'CACHE_OPTIONS': {'behaviors': {
                               # Faster IO
                               'tcp_nodelay': True,
                               # Keep connection alive
                               'tcp_keepalive': True,
                               # Timeout for set/get requests
                               'connect_timeout': 2000,  # ms
                               'send_timeout': 750 * 1000,  # us
                               'receive_timeout': 750 * 1000,  # us
                               '_poll_timeout': 2000,  # ms
                               # Better failover
                               'ketama': True,
                               'remove_failed': 1,
                               'retry_timeout': 2,
                               'dead_timeout': 30}}})


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


def chunks3(xs, n):
    n = max(1, n)
    coordinate_list = []
    for i in range(0, len(xs), n):
        coordinate_list.append(xs[i:i + n])
    for t in coordinate_list:
        ind = coordinate_list.index(t)
        coordinate_list[ind] = [float(t[1]), float(t[0])]
    return coordinate_list

@cache.memoize()
def read_all():
    """
    This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
    LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
    WGS84. Also caution for file paths especially having space in it.

    """
    maps = folium.Map(location=[39, 35], zoom_start=6)
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    mcg = folium.plugins.MarkerCluster(control=False)
    maps.add_child(mcg)
    sql_enr = "SELECT * FROM enr_obstacles"
    df_enr = pd.read_sql(sql_enr, con=engine)
    df_enr['geometry'] = df_enr['geo'].apply(wkt.loads)
    ydf = geopandas.GeoDataFrame(df_enr, crs='EPSG:4326')
    g0 = folium.plugins.FeatureGroupSubGroup(mcg, 'ENR Obstacles')
    maps.add_child(g0)
    for y in range(ydf.shape[0]):
        coo = ydf.loc[y, 'geometry']
        # icons = folium.CustomIcon(
        #     icon_image='/app/static/assets/images/marker_dot.png')
        marker = folium.CircleMarker(location=(coo.y, coo.x), radius=3, color='purple', fill_opacity=1, fill=True)
        popup = (f"Elevation: {ydf.loc[y, 'elevation']} FT Type: {ydf.loc[y, 'type']} "
                 f" Coordinates: {coo.y}N, {coo.x}E")

        folium.Popup(popup).add_to(marker)
        marker.add_to(g0)
    sql_ad = "SELECT * FROM ad_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    cdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    g1 = folium.plugins.FeatureGroupSubGroup(mcg, 'Ad_Obs')
    maps.add_child(g1)
    for o in range(cdf.shape[0]):
        coor = cdf.get_coordinates(ignore_index=True)
        # icons = folium.CustomIcon(
        #     icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/marker_dot.png')
        marker = folium.CircleMarker(location=[coor.loc[o, 'y'], coor.loc[o, 'x']], radius=3, color='purple', fill_opacity=1, fill=True)
        popup = (f"Elevation: {cdf.loc[o, 'elevation']} FT Type: {cdf.loc[o, 'type']} "
                 f" Coordinates: {coor.loc[o, 'y']}N, {coor.loc[o, 'x']}E")

        folium.Popup(popup).add_to(marker)
        marker.add_to(g1)

    sql_a2 = "SELECT * FROM area2a_obstacles"
    df_a2 = pd.read_sql(sql_a2, con=engine)
    df_a2['geometry'] = df_a2['geo'].apply(wkt.loads)
    bdf = geopandas.GeoDataFrame(df_a2, crs='EPSG:4326')
    g2 = folium.plugins.FeatureGroupSubGroup(mcg, 'Area2a Obst')
    maps.add_child(g2)

    for o in range(bdf.shape[0]):
        coor = bdf.get_coordinates(ignore_index=True)

        if bdf.loc[o, 'geometry'].geom_type == 'Point':
            yy = bdf.loc[o, 'coordinate'].replace(',', '.').split(' ')
            # icons = folium.CustomIcon(
            #     icon_image='/app/static/assets/images/marker_dot.png')
            marker = folium.CircleMarker(location=[yy[0], yy[1]], radius=3, color='blue',
                                         fill_opacity=1, fill=True)
            popup = (f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[o, 'y']}N, {coor.loc[o, 'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g2)
        elif bdf.loc[o, 'geometry'].geom_type == 'MultiLineString':
            folium.PolyLine(locations=chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='red',
                            popup=f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
                                  f" Coordinates(..N..E): {chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g2)

    sql_a3 = "SELECT * FROM area3_obstacles"
    df_a3 = pd.read_sql(sql_a3, con=engine)
    df_a3['geometry'] = df_a3['geo'].apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df_a3, crs='EPSG:4326')

    g3 = folium.plugins.FeatureGroupSubGroup(mcg, 'Area3_Obst')
    maps.add_child(g3)
    coords = gdf.get_coordinates(ignore_index=True)
    for t in range(gdf.shape[0]):

        if gdf.loc[t, 'geometry'].geom_type == 'Point':
            oo= gdf.loc[t, 'coordinate'].replace(',', '.').split(' ')
            # icons = folium.CustomIcon(
            #     icon_image='/app/static/assets/images/marker_dot.png')
            marker = folium.CircleMarker(location=[oo[0], oo[1]], radius=3, color='magenta',
                                         fill_opacity=1, fill=True)
            popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                     f" Coordinates: {coords.loc[t, 'y']}N, {coords.loc[t, 'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g3)

        elif gdf.loc[t, 'geometry'].geom_type == 'MultiLineString':
            folium.PolyLine(locations=chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='purple',
                            popup=f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                                  f" Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g3)

    sql_ltac = "SELECT * FROM ltac_area3_obstacles"
    df_ltac = pd.read_sql(sql_ltac, con=engine)
    df_ltac['geometry'] = df_ltac['geo'].apply(wkt.loads)
    ltac = geopandas.GeoDataFrame(df_ltac, crs='EPSG:4326')
    # g6 = folium.plugins.FeatureGroupSubGroup(mcg, 'LTAC Area3 Obst')
    # maps.add_child(g6)
    coord = ltac.get_coordinates(ignore_index=True)
    for e in range(ltac.shape[0]):

        if ltac.loc[e, 'geometry'].geom_type == 'Point':
            uu = ltac.loc[e, 'Coordinate'].replace(',', '.').split(' ')
            # icons = folium.CustomIcon(
            #     icon_image='/app/static/assets/images/marker_dot.png')
            marker = folium.CircleMarker(location=[uu[0], uu[1]], radius=3, color='pink',
                                         fill_opacity=1, fill=True)
            popup = (f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}"
                     f" Coordinates: {coord.loc[e, 'y']}N, {coord.loc[e, 'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g3)

        elif ltac.loc[e, 'geometry'].geom_type == 'LineString':
            folium.PolyLine(locations=chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                            color='brown',
                            popup=f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']} "
                                  f" Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g3)


        elif ltac.loc[e, 'geometry'].geom_type == 'Polygon':
            folium.Polygon(locations=chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                           color='brown',
                           popup=f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']} "
                                 f" Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g3)
    sql_a4 = "SELECT * FROM area4_obstacles"
    df_a4 = pd.read_sql(sql_a4, con=engine)
    df_a4['geometry'] = df_a4['geo'].apply(wkt.loads)
    hdf = geopandas.GeoDataFrame(df_a4, crs='EPSG:4326')

    g4 = folium.plugins.FeatureGroupSubGroup(mcg, 'Area4_Obst')
    maps.add_child(g4)

    for l in range(hdf.shape[0]):
        coordss = hdf.get_coordinates(ignore_index=True)
        if len(hdf.loc[l, 'coordinate']) % 2 != 0:
            hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]

        if hdf.loc[l, 'coordinate'][-4::1] == ' 38*':
            hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-4]

        if hdf.loc[l, 'geometry'].geom_type == 'Point':
            c = hdf.loc[l, 'coordinate'].replace(',', '.').split(' ')
            # icons = folium.CustomIcon(
            #     icon_image='/app/static/assets/images/marker_dot.png')
            marker = folium.CircleMarker(location=[c[0], c[1]], radius=3, color='black',
                                         fill_opacity=1, fill=True)
            popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                     f" Coordinates: {coordss.loc[l, 'y']}N, {coordss.loc[l, 'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g4)

        elif hdf.loc[l, 'geometry'].geom_type == 'MultiLineString':

            folium.PolyLine(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='green',
                            popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                                  f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g4)

    sql_fm = "SELECT * FROM ltfm_area4_obstacles"
    df_fm = pd.read_sql(sql_fm, con=engine)
    df_fm['geometry'] = df_fm['geo'].apply(wkt.loads)
    xdf = geopandas.GeoDataFrame(df_fm, crs='EPSG:4326')

    # g5 = folium.plugins.FeatureGroupSubGroup(mcg, 'Ltfm_Area4_Obstacles')
    # maps.add_child(g5)

    for u in range(xdf.shape[0]):
        coorddss = xdf.get_coordinates(ignore_index=True)
        if xdf.loc[u, 'geometry'].geom_type == 'Point':
            gg = xdf.loc[u, 'coordinate'].replace(',', '.').split(' ')
            # icons = folium.CustomIcon(
            #     icon_image='/app/static/assets/images/marker_dot.png')
            marker = folium.CircleMarker(location=[gg[0], gg[1]], radius=3,
                                         color='yellow', fill_opacity=1, fill=True)
            popup = (f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}"
                     f" Coordinates: {coorddss.loc[u, 'y']}N, {coorddss.loc[u, 'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g4)

        elif xdf.loc[u, 'geometry'].geom_type == 'MultiLineString':
            folium.PolyLine(locations=chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='brown',
                            popup=f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']} "
                                  f" Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g4)


        elif xdf.loc[u, 'geometry'].geom_type == 'MultiPolygon':
            folium.Polygon(locations=chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
                           color='brown',
                           popup=f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']} "
                                 f" Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g4)

    folium.LayerControl(collapsed=False).add_to(maps)
    folium.plugins.MousePosition().add_to(maps)
    frame = maps.get_root().render()
    return frame


@app.route('/all', methods=['GET', 'POST'])
@cache.cached()
def all():

    frame = read_all()

    return render_template('mapping.html', iframe=frame, title='All Obstacles | Folium')


def marker_creator_ad_2(df, i):
    if 'BUILDING' in df.loc[i, 'name'] or 'BULDING' in df.loc[i, 'name']:
        # kw = {"prefix": "fa", "color": "green", "icon": "building"}
        # icons = folium.Icon(**kw)
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/building.png')


    elif 'MAST' in df.loc[i, 'name']:
        if df.loc[i, 'name'] == 'LIGHTING MAST':
            # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/street-light.png')

        elif df.loc[i, 'name'] == 'APRON LIGHTING MAST' or df.loc[i, 'name'] == 'APRON LIGTHING MAST':
            # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/apron_lighting.png')

        else:
            icons = folium.CustomIcon(icon_image='/app/static/assets/images/mast.png')
            # folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/aixm_mapping/icons8-pylon-64.png')



    elif df.loc[i, 'name'] == 'MOSQUE' or df.loc[i, 'name'] == 'MOSQUE_DOME':

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/mosque.png')


    elif df.loc[i, 'name'] == 'MINARET':

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/minaret.png')

    elif 'SURVEILLANCE TOWER' in df.loc[i, 'name'] or 'TWR' in df.loc[i, 'name'] or 'TOWER' in df.loc[
        i, 'name']:
        kw = {"prefix": "fa", "color": "pink", "icon": "tower-observation"}
        icons = folium.Icon(**kw)

    elif 'ANTENNA' in df.loc[i, 'name']:
        if df.loc[i, 'name'] == 'GSM ANTENNA':
            # kw = {"prefix": "fa", "color": "purple", "icon": "signal"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/gsm_anten.png')

        elif df.loc[i, 'name'] == 'DME ANTENNA' or df.loc[i, 'name'] == 'DME ANTENNA(GP)':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/dme_antenna.png')

        elif df.loc[i, 'name'] == 'GLIDE PATH  ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA' \
                or df.loc[i, 'name'] == 'GP ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/glidepath_antenna.png')

        elif df.loc[i, 'name'] == 'LLZ ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/llz_ant.png')

        elif df.loc[i, 'name'] == 'NDB ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/ndb_antenna.png')

        elif df.loc[i, 'name'] == 'TACAN ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/tacan_antenna.png')

        elif df.loc[i, 'name'] == 'VOR ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/vor_antenna.png')

        elif df.loc[i, 'name'] == 'NF ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/nf_antenna.png')

        else:
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/antenna.png')

    elif df.loc[i, 'name'] == 'CHIMNEY' or df.loc[i, 'name'] == 'SHAFT':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/chimney.png')

    elif df.loc[i, 'name'] == 'ANM' or 'ANEMO' in df.loc[i, 'name']:
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/anemometer.png')


    elif 'WIND' in df.loc[i, 'name']:
        if 'DIRECTION' in df.loc[i, 'name']:
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/wind-direction.png')

        elif 'ROSE' in df.loc[i, 'name']:
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/wind-rose.png')


        elif 'TURBINE' in df.loc[i, 'name'] or 'T' in df.loc[i, 'name']:
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/wind-turbine.png')


        else:
            icons = folium.CustomIcon(
                icon_image='/app/static/assets/images/windsock.png')


    elif 'WDI' in df.loc[i, 'name']:
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/wind-direction.png')

    elif 'APPROACH' in df.loc[i, 'name']:
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/landing-track.png')

    elif 'POLE' in df.loc[i, 'name']:
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/pole.png')


    elif df.loc[i, 'name'] == 'LIGHTNING ROD' or df.loc[i, 'name'] == 'PARATONER' or df.loc[
        i, 'name'] == 'PARATONNERRE':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/lightning-rod.png')


    elif df.loc[i, 'name'] == 'HOSPITAL':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/hospital.png')


    elif df.loc[i, 'name'] == 'DME' or df.loc[i, 'name'] == 'DME ILS/GP':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/dme.png')


    elif df.loc[i, 'name'] == 'NDB':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/ndb.png')


    elif df.loc[i, 'name'] == 'TACAN' or df.loc[i, 'name'] == 'TACAN CONTAINER':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/tacan.png')


    elif df.loc[i, 'name'] == 'VOR' or df.loc[i, 'name'] == 'VOR CONTAINER' or df.loc[
        i, 'name'] == 'VOR STATION':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/vor.png')


    elif df.loc[i, 'name'] == 'VOR+DME' or df.loc[i, 'name'] == 'VOR/DME':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/vor_dme.png')


    elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/nf_antenna.png')


    elif 'LIGHT' in df.loc[i, 'name']:

        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/street-light.png')


    elif df.loc[i, 'name'] == 'GREENHOUSE' or df.loc[i, 'name'] == 'GREEN HOUSE' or df.loc[
        i, 'name'] == 'PLANT-HOUSE' or df.loc[i, 'name'] == 'GARDEN FRAME':

        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/greenhouse.png')

    elif df.loc[i, 'name'] == 'SILO' or df.loc[i, 'name'] == 'GRAIN SILO':

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/silo.png')


    elif df.loc[i, 'name'] == 'STADIUM':

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/stadium.png')


    elif 'HOOK BARRIER' in df.loc[i, 'name']:

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/hook.png')


    elif 'NET BARRIER' in df.loc[i, 'name']:

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/net.png')


    elif df.loc[i, 'name'] == 'CONCRETE BARRIER' or df.loc[i, 'name'] == 'CONCRETE BLOCK' or df.loc[
        i, 'name'] == 'BETON BARIYER':

        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/concrete_barrier.png')


    elif 'WALL' in df.loc[i, 'name']:

        icons = folium.CustomIcon(icon_image='/app/static/assets/images/wall.png')


    elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/nf_antenna.png')


    elif (df.loc[i, 'name'] == 'DVOR' or df.loc[i, 'name'] == 'DVOR_LC' or df.loc[i, 'name'] == 'DVOR_MONITOR'
          or df.loc[i, 'name'] == 'FFM_18' or df.loc[i, 'name'] == 'FFM_17L' or df.loc[i, 'name'] == 'FFM-35R'
          or df.loc[i, 'name'] == "FFM_34L" or df.loc[i, 'name'] == 'FFM_36' or df.loc[
              i, 'name'] == 'GLIDE PATH'
          or df.loc[i, 'name'] == 'GLIDEPAT CON.' or df.loc[i, 'name'] == 'GLIDE PATH SHELTER' or df.loc[
              i, 'name'] == 'GLIDE PATH CONTAINER'
          or df.loc[i, 'name'] == 'GP' or df.loc[i, 'name'] == 'GP CABIN' or df.loc[i, 'name'] == 'GP STATION'
          or df.loc[i, 'name'] == 'GP_16R_MONITOR' or df.loc[i, 'name'] == 'GP/NAVAID' or df.loc[
              i, 'name'] == 'GP/DME'
          or df.loc[i, 'name'] == 'GP_16R_OBS_LT' or df.loc[i, 'name'] == 'GP_17L_MONITOR' or df.loc[
              i, 'name'] == 'GP_17L_OBS_LT'
          or df.loc[i, 'name'] == 'GP_34L_MONITOR' or df.loc[i, 'name'] == 'GP_18_OBS_LT' or df.loc[
              i, 'name'] == 'GP_18_MONITOR'
          or df.loc[i, 'name'] == 'GP_34L_OBS_LT' or df.loc[i, 'name'] == 'GP_35R_MONITOR' or df.loc[
              i, 'name'] == 'GP_35R_OBS_LT'
          or df.loc[i, 'name'] == 'LLZ CON.' or df.loc[i, 'name'] == 'GP_36_OBS_LT' or df.loc[
              i, 'name'] == 'GP_36_MONITOR'
          or df.loc[i, 'name'] == 'LLZ CONTAINER' or df.loc[i, 'name'] == 'LLZ16' or df.loc[
              i, 'name'] == 'LLZ_18'
          or df.loc[i, 'name'] == 'RVR' or df.loc[i, 'name'] == 'PAPI_COVER' or df.loc[
              i, 'name'] == 'LOCALIZER' or
          df.loc[i, 'name'] == 'RAPCON'
          or df.loc[i, 'name'] == 'RVR-SENSOR') or df.loc[i, 'name'] == 'NDB FIELD' or df.loc[
        i, 'name'] == 'GCA' or \
            df.loc[i, 'name'] == 'SENTRY BOX' \
            or df.loc[i, 'name'] == 'NFM_34L':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/other_navigation_aid.png')

    elif df.loc[i, 'name'] == 'GSM BASE STATION' or df.loc[i, 'name'] == 'GSM STATION':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/gsm_anten.png')


    elif df.loc[i, 'name'] == 'GAS STATION':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/gas-station.png')


    elif df.loc[i, 'name'] == 'RADAR_STATION':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/radar.png')


    elif (df.loc[i, 'name'] == 'CABIN' or df.loc[i, 'name'] == 'CONSTRUCTION' or df.loc[i, 'name'] == 'COTTAGE'
          or df.loc[i, 'name'] == 'GUARD COTTAGE' or df.loc[i, 'name'] == 'STRUCTURE'):
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/cabin.png')


    elif df.loc[i, 'name'] == 'HANGAR':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/hangar.png')


    elif df.loc[i, 'name'] == 'MILITARY TRENCH':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/trench.png')


    elif df.loc[i, 'name'] == 'REFLECTOR':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/reflector.png')


    elif df.loc[i, 'name'] == 'ROCK' or df.loc[i, 'name'] == 'STACK' \
            or df.loc[i, 'name'] == 'CLIFF':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/rock_stack_cliff.png')


    elif df.loc[i, 'name'] == 'TREE':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/tree.png')


    elif df.loc[i, 'name'] == 'VAN CASTLE':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/castle.png')


    elif df.loc[i, 'name'] == 'BRIDGE_DECK':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/bridge_deck.png')


    elif df.loc[i, 'name'] == 'TRANSFORMER':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/transformer.png')


    elif df.loc[i, 'name'] == 'TRAFFIC_SIGN' or df.loc[i, 'name'] == 'TRAFFIC BOARD' \
            or df.loc[i, 'name'] == 'SIGNBOARD':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/sign_board.png')


    elif df.loc[i, 'name'] == 'PYLON':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/pylon.png')


    elif df.loc[i, 'name'] == 'CRANE':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/crane.png')


    elif df.loc[i, 'name'] == 'ARFF POOL':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/arff_pool.png')


    elif df.loc[i, 'name'] == 'ENERGY TRANSMISSION LINE' or df.loc[i, 'name'] == 'POWER_TRANSMISSION_LINE':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/transmission.png')

    elif df.loc[i, 'name'] == 'CONTAINER':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/container.png')


    elif 'TERRAIN' in df.loc[i, 'name']:
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/terrain.png')


    elif df.loc[i, 'name'] == 'BASE STATION':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/base_station.png')


    elif df.loc[i, 'name'] == 'BILLBOARD':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/billboard.png')


    elif df.loc[i, 'name'] == 'CAMERA PANEL':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/panel.png')


    elif df.loc[i, 'name'] == 'FENCE' or df.loc[i, 'name'] == 'WIRE FENCE':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/fence.png')


    elif df.loc[i, 'name'] == 'FUEL_TANK':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/fuel_tank.png')


    elif df.loc[i, 'name'] == 'WATER TANK':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/water_tank.png')


    elif df.loc[i, 'name'] == 'WATER ROSERVOIR':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/reservoir.png')


    elif df.loc[i, 'name'] == 'ENERGY CABIN':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/energy_cabin.png')


    elif df.loc[i, 'name'] == 'METEOROLOGY DEVICE':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/meteo_device.png')


    elif df.loc[i, 'name'] == 'OKIS':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/okis.png')


    elif df.loc[i, 'name'] == 'TERMINAL':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/terminal.png')


    elif df.loc[i, 'name'] == 'VOICE BIRD SCARING SYSTEM':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/vbss.png')


    elif df.loc[i, 'name'] == 'WATCH BOX':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/watch_box.png')


    elif df.loc[i, 'name'] == 'GNSS_MEASUREMENT_POINT':
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/gnss.png')

    elif df.loc[i, 'name'] == 'OTHER':
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/other_navigation_aid.png')

    else:
        icons = folium.CustomIcon(icon_image='/app/static/assets/images/laughing.png')

    return icons


# create_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
# create_area_3_4_db(path_list_area_4,4, path_list_area_4_xml)
@app.route("/", methods=['GET', 'POST'])
@cache.cached()
def fullscreen():
    m = folium.Map(location=[39, 35], zoom_start=6)
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    sql_ad = "SELECT * FROM ad_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    df = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    # for p in path_list_ad[:]:
    mcg = MarkerCluster(name='AD_Obst', control=True)
    for i in range(df.shape[0]):
        # if df.loc[i, 'aerodrome'] == str(p)[64:68].lower():
        coor = df.loc[i, 'coordinate'].replace(',', '.').split(' ')
        icons = marker_creator_ad_2(df, i)
        marker = folium.Marker(location=(coor[1], coor[0]), icon=icons)
        popup = (f"Elevation: {df.loc[i, 'elevation']} FT Type: {df.loc[i, 'type']} "
                 f" Coordinates: {coor[1]}N, {coor[0]}E")

        folium.Popup(popup).add_to(marker)
        mcg.add_child(marker)
    mcg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    """Simple example of a fullscreen map."""
    folium.plugins.MousePosition().add_to(m)
    frame = m.get_root().render()

    return render_template('mapping.html', iframe=frame, title='Fullscreen AD Map | Folium')


@app.route("/aerodrome", methods=['GET', 'POST'])
@cache.cached()
def ad():
    m = folium.Map(location=[39, 35], zoom_start=6)
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    sql_ad = "SELECT * FROM ad_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    df = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    # dict_ad = {}
    # for p in path_list_ad[:]:
    #     dict_ad[str(p)[64:68] + '_AD_Obstacles'] = MarkerCluster(name=str(p)[64:68] + '_AD_Obstacles', control=True)
    mc = MarkerCluster(name='AD_Obstacles', control=True)
    for i in range(df.shape[0]):

        coor = df.loc[i, 'coordinate'].replace(',', '.').split(' ')
        #icons = marker_creator_ad_2(df, i)
        marker = folium.CircleMarker(location=(coor[1], coor[0]), radius=3, color='red',
                                     fill=True, fill_opacity=0.5)
        popup = (f"Elevation: {df.loc[i, 'elevation']} FT Type: {df.loc[i, 'type']} "
                 f" Coordinates: {coor[1]}N, {coor[0]}E")

        folium.Popup(popup).add_to(marker)
        mc.add_child(marker)
        mc.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    """Simple example of a fullscreen map."""
    folium.plugins.MousePosition().add_to(m)
    frame = m.get_root().render()

    return render_template('mapping.html', iframe=frame, title=' AD Map | Folium')


m50 = folium.Map(location=[39, 35], zoom_start=6)


@app.route("/enrobs", methods=['GET', 'POST'])
def enr_obstacles():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    maps = folium.Map(location=[39, 35], zoom_start=6)
    mcg = folium.plugins.MarkerCluster(control=False)
    maps.add_child(mcg)
    sql_enr = "SELECT * FROM enr_obstacles"
    df_enr = pd.read_sql(sql_enr, con=engine)
    df_enr['geometry'] = df_enr['geo'].apply(wkt.loads)
    ydf = geopandas.GeoDataFrame(df_enr, crs='EPSG:4326')
    g0 = folium.plugins.FeatureGroupSubGroup(mcg, 'ENR Obstacles')
    maps.add_child(g0)
    for y in range(ydf.shape[0]):
        coo = ydf.loc[y, 'geometry']
        # icons = folium.CustomIcon(
        #     icon_image='/app/static/assets/images/marker_dot.png')
        marker = folium.CircleMarker(location=(coo.y, coo.x), radius=3, color='purple', fill_opacity=1, fill=True)
        popup = (f"Elevation: {ydf.loc[y, 'elevation']} FT Type: {ydf.loc[y, 'type']} "
                 f" Coordinates: {coo.y}N, {coo.x}E")

        folium.Popup(popup).add_to(marker)
        marker.add_to(g0)
    folium.plugins.MousePosition().add_to(maps)
    folium.LayerControl(collapsed=False).add_to(maps)

    frame = maps.get_root().render()

    return render_template('mapping.html', iframe=frame, title='ENR Obstacles | Folium')


@app.route('/area2a', methods=['GET', 'POST'])
@cache.cached()
def area_2a_obstacles():
    m4 = folium.Map(location=[39, 35], zoom_start=6)
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    sql_ad = "SELECT * FROM area2a_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    # dict_area2 = {}
    # for p in path_list_area_2[:]:
    #     dict_area2[str(p)[61:65].lower() + '_Area2a_Obstacles'] = MarkerCluster(name=str(p)[61:65] + '_Area2a_Obstacles', control=True)
    mc = MarkerCluster(name='Area2a_Obstacles', control=True)
    for i in range(gdf.shape[0]):

        coor = gdf.get_coordinates(ignore_index=True)
        if gdf.loc[i, 'geometry'].geom_type == 'Point':
            hh = gdf.loc[i, 'coordinate'].replace(',', '.').split(' ')
            marker = folium.CircleMarker(location=(hh[0], hh[1]), radius=3, color='red',
                                         fill=True, fill_opacity=1)
            popup = (f"Elevation: {gdf.loc[i, 'elevation']} FT Type: {gdf.loc[i, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[i, 'y']}N, {coor.loc[i, 'x']}E")

            folium.Popup(popup).add_to(marker)

            mc.add_child(marker)

        elif gdf.loc[i, 'geometry'].geom_type == 'MultiLineString':
            poly = folium.PolyLine(locations=chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                                   color='purple',
                                   popup=f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} "
                                         f" Coordinates(..N..E): {chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}")
            mc.add_child(poly)
        elif gdf.loc[i, 'geometry'].geom_type == 'MultiPolygon':
            sky = folium.Polygon(locations=chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                           color='purple',
                           popup=f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} "
                                 f" Coordinates(..N..E): {chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}")
            mc.add_child(sky)
        mc.add_to(m4)
    folium.plugins.MousePosition().add_to(m4)
    folium.LayerControl(collapsed=False).add_to(m4)
    frame = m4.get_root().render()

    return render_template('mapping.html', iframe=frame, title='Area 2A Obstacles | Folium')


@app.route('/area3', methods=['GET', 'POST'])
def area_3():
    m5 = folium.Map(location=[39, 35], zoom_start=6)
    mcg = folium.plugins.MarkerCluster(control=False)
    m5.add_child(mcg)
    g6 = folium.plugins.FeatureGroupSubGroup(mcg, 'LTAC_Area3_Obst')
    m5.add_child(g6)
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    sql_ad = "SELECT * FROM ltac_area3_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    ltac = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    for e in range(ltac.shape[0]):
        coor = ltac.get_coordinates(ignore_index=True)
        if ltac.loc[e, 'geometry'].geom_type == 'Point':
            # icons = folium.CustomIcon(
            #     icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/marker_dot.png')
            marker = folium.CircleMarker(location=(coor.loc[e, 'x'], coor.loc[e, 'y']), radius=3, color='brown', fill=True, fill_opacity=1)
            popup = (f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}"
                     f" Coordinates: {coor.loc[e, 'x']}N, {coor.loc[e, 'y']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g6)

        elif ltac.loc[e, 'geometry'].geom_type == 'LineString':
            folium.PolyLine(locations=chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                            color='brown',
                            popup=f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']} "
                                  f" Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g6)


        elif ltac.loc[e, 'geometry'].geom_type == 'Polygon':
            folium.Polygon(locations=chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                           color='brown',
                           popup=f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']} "
                                 f" Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g6)
    sql_ad = "SELECT * FROM area3_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    # for i in path_list_area_3:
    #     layer_name = str(i)[69:73].replace('/', '_').replace('.gdb', '').lower() + '_Area3_Obstacles'
    g5 = folium.plugins.FeatureGroupSubGroup(mcg,  'Other_Area3_Obst')
    m5.add_child(g5)
    for t in range(gdf.shape[0]):

        coor = gdf.get_coordinates(ignore_index=True)
        icons = folium.CustomIcon(
            icon_image='/app/static/assets/images/marker_dot.png')
        if gdf.loc[t, 'geometry'].geom_type == 'Point':
            coordddd = gdf.loc[t, 'coordinate'].replace(',', '.').split(' ')
            marker = folium.CircleMarker(location=(coordddd[0], coordddd[1]), radius=3, color='red',fill=True, fill_opacity=1)
            popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[t, 'y']}N, {coor.loc[t, 'x']}E")
            folium.Popup(popup).add_to(marker)
            marker.add_to(g5)

        elif gdf.loc[t, 'geometry'].geom_type == 'MultiLineString':
            folium.PolyLine(locations=chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='purple',
                            popup=f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                                  f" Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g5)

    folium.LayerControl(collapsed=False).add_to(m5)
    folium.plugins.MousePosition().add_to(m5)
    frame = m5.get_root().render()
    return render_template('mapping.html', iframe=frame, title='Area 3 Obstacles | Folium')


@app.route('/area4')
def area_4():
    m6 = folium.Map(location=[39, 35], zoom_start=6)
    mcg = MarkerCluster(control=False)
    m6.add_child(mcg)
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    sql_ad = "SELECT * FROM area4_obstacles"
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    hdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    # for u in path_list_area_4:
    #     layer_name = str(u)[69:].replace('/', '_').replace('.gdb', '').lower() + "_Area4_Obstacles"
    g7 = folium.plugins.FeatureGroupSubGroup(mcg, 'Other_Area4_Obst')
    m6.add_child(g7)

    for l in range(hdf.shape[0]):


        if hdf.loc[l, 'obstacle_identifier'] == '792-55-A1-R1-40-0013':
            hdf.loc[l, 'coordinate'] = ('41.268954490 36.545948667 41.268945407 36.545976610 41.268935298 '
                                        '36.546001687 41.268911937 36.545996773 41.268906594 36.546008163 '
                                        '41.268860851 36.545985842 41.268873754 36.545940854 41.268895308 '
                                        '36.545889963 41.268915084 36.545843271 41.268954558 36.545870598 '
                                        '41.268935405 36.545917174 41.268929546 36.545931420 41.268954490 '
                                        '36.545948667')
        if hdf.loc[l, 'geometry'].geom_type == 'MultiLineString':
            if len(hdf.loc[l, 'coordinate']) % 2 != 0:
                hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]

            if hdf.loc[l, 'coordinate'][-4::1] == ' 38*':
                hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-4]

            if hdf.loc[l, 'aerodrome'] == 'ltfe_area_4_area_4_28r_area_4_28r_Area4_Obstacles':
                folium.PolyLine(locations=chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                color='green',
                                popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                                      f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                    g7)
            else:
                folium.PolyLine(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                color='green',
                                popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                                      f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                    g7)



        elif hdf.loc[l, 'geometry'].geom_type == 'MultiPolygon':
            if len(hdf.loc[l, 'coordinate']) % 2 != 0:
                hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]

            if hdf.loc[l, 'aerodrome'] == 'ltfe_area_4_area_4_28r_area_4_28r_Area4_Obstacles':
                folium.Polygon(locations=chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                               color='green',
                               popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                                     f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                    g7)
            else:
                folium.Polygon(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                               color='blue',
                               popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                                     f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                    g7)

        elif hdf.loc[l, 'geometry'].geom_type == 'Point':

            coor = hdf.loc[l, 'coordinate'].replace(',', '.').split(' ')

            marker = folium.CircleMarker(location=[coor[0], coor[1]], radius=3, color='red', fill=True, stroke=False,
                                         fill_opacity=1)
            popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                     f" Coordinates: {coor[0]}N, {coor[1]}E")
            folium.Popup(popup).add_to(marker)
            marker.add_to(g7)

    sql_fm = "SELECT * FROM ltfm_area4_obstacles"
    df_fm = pd.read_sql(sql_fm, con=engine)
    df_fm['geometry'] = df_fm['geo'].apply(wkt.loads)
    xdf = geopandas.GeoDataFrame(df_fm, crs='EPSG:4326')
    g8 = FeatureGroupSubGroup(mcg, "LTFM_Area4_Obstacles")
    g8.add_to(m6)
    for e in range(xdf.shape[0]):
        coor = xdf.get_coordinates(ignore_index=True)
        if xdf.loc[e, 'geometry'].geom_type == 'Point':
            marker = folium.CircleMarker(location=[coor.loc[e, 'y'], coor.loc[e, 'x']], radius=3, color='red',
                                         fill_opacity=1, fill=True)
            popup = (f"Elevation: {xdf.loc[e, 'elevation']} FT  Type: {xdf.loc[e, 'type']}"
                     f" Coordinates: {coor.loc[e, 'y']}N, {coor.loc[e, 'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g8)

        elif xdf.loc[e, 'geometry'].geom_type == 'MultiLineString':
            folium.PolyLine(locations=chunks2(xdf.loc[e, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='brown',
                            popup=f"Elevation: {xdf.loc[e, 'elevation']} FT  Type: {xdf.loc[e, 'type']} "
                                  f" Coordinates(..N..E): {chunks2(xdf.loc[e, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g8)


        elif xdf.loc[e, 'geometry'].geom_type == 'MultiPolygon':
            folium.Polygon(locations=chunks2(xdf.loc[e, 'coordinate'].replace(',', '.').split(' '), 2),
                           color='brown',
                           popup=f"Elevation: {xdf.loc[e, 'elevation']} FT  Type: {xdf.loc[e, 'type']} "
                                 f" Coordinates(..N..E): {chunks2(xdf.loc[e, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
                g8)

    folium.plugins.MousePosition().add_to(m6)
    folium.LayerControl(collapsed=False).add_to(m6)
    frame = m6.get_root().render()

    return render_template('mapping.html', iframe=frame, title='Area 4 Obstacles | Folium')


def marker_creator_ad(df, i):
    if 'BUILDING' in df.loc[i, 'name'] or 'BULDING' in df.loc[i, 'name']:
        # kw = {"prefix": "fa", "color": "green", "icon": "building"}
        # icons = folium.Icon(**kw)
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/building.png')


    elif 'MAST' in df.loc[i, 'name']:
        if df.loc[i, 'name'] == 'LIGHTING MAST':
            # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/street-light.png')

        elif df.loc[i, 'name'] == 'APRON LIGHTING MAST' or df.loc[i, 'name'] == 'APRON LIGTHING MAST':
            # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/apron_lighting.png')

        else:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/mast.png')
            # folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/aixm_mapping/icons8-pylon-64.png')



    elif df.loc[i, 'name'] == 'MOSQUE' or df.loc[i, 'name'] == 'MOSQUE_DOME':

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/mosque.png')


    elif df.loc[i, 'name'] == 'MINARET':

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/minaret.png')

    elif 'SURVEILLANCE TOWER' in df.loc[i, 'name'] or 'TWR' in df.loc[i, 'name'] or 'TOWER' in df.loc[
        i, 'name']:
        kw = {"prefix": "fa", "color": "pink", "icon": "tower-observation"}
        icons = folium.Icon(**kw)

    elif 'ANTENNA' in df.loc[i, 'name']:
        if df.loc[i, 'name'] == 'GSM ANTENNA':
            # kw = {"prefix": "fa", "color": "purple", "icon": "signal"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/gsm_anten.png')

        elif df.loc[i, 'name'] == 'DME ANTENNA' or df.loc[i, 'name'] == 'DME ANTENNA(GP)':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/dme_antenna.png')

        elif df.loc[i, 'name'] == 'GLIDE PATH  ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA' \
                or df.loc[i, 'name'] == 'GP ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/glidepath_antenna.png')

        elif df.loc[i, 'name'] == 'LLZ ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/llz_ant.png')

        elif df.loc[i, 'name'] == 'NDB ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/ndb_antenna.png')

        elif df.loc[i, 'name'] == 'TACAN ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/tacan_antenna.png')

        elif df.loc[i, 'name'] == 'VOR ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/vor_antenna.png')

        elif df.loc[i, 'name'] == 'NF ANTENNA':
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/nf_antenna.png')

        else:
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/antenna.png')

    elif df.loc[i, 'name'] == 'CHIMNEY' or df.loc[i, 'name'] == 'SHAFT':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/chimney.png')

    elif df.loc[i, 'name'] == 'ANM' or 'ANEMO' in df.loc[i, 'name']:
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/anemometer.png')


    elif 'WIND' in df.loc[i, 'name']:
        if 'DIRECTION' in df.loc[i, 'name']:
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/wind-direction.png')

        elif 'ROSE' in df.loc[i, 'name']:
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/wind-rose.png')


        elif 'TURBINE' in df.loc[i, 'name'] or 'T' in df.loc[i, 'name']:
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/wind-turbine.png')


        else:
            icons = folium.CustomIcon(
                icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/windsock.png')


    elif 'WDI' in df.loc[i, 'name']:
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/wind-direction.png')

    elif 'APPROACH' in df.loc[i, 'name']:
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/landing-track.png')

    elif 'POLE' in df.loc[i, 'name']:
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/pole.png')


    elif df.loc[i, 'name'] == 'LIGHTNING ROD' or df.loc[i, 'name'] == 'PARATONER' or df.loc[
        i, 'name'] == 'PARATONNERRE':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/lightning-rod.png')


    elif df.loc[i, 'name'] == 'HOSPITAL':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/hospital.png')


    elif df.loc[i, 'name'] == 'DME' or df.loc[i, 'name'] == 'DME ILS/GP':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/dme.png')


    elif df.loc[i, 'name'] == 'NDB':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/ndb.png')


    elif df.loc[i, 'name'] == 'TACAN' or df.loc[i, 'name'] == 'TACAN CONTAINER':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/tacan.png')


    elif df.loc[i, 'name'] == 'VOR' or df.loc[i, 'name'] == 'VOR CONTAINER' or df.loc[
        i, 'name'] == 'VOR STATION':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor.png')


    elif df.loc[i, 'name'] == 'VOR+DME' or df.loc[i, 'name'] == 'VOR/DME':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/vor_dme.png')


    elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/nf_antenna.png')


    elif 'LIGHT' in df.loc[i, 'name']:

        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/street-light.png')


    elif df.loc[i, 'name'] == 'GREENHOUSE' or df.loc[i, 'name'] == 'GREEN HOUSE' or df.loc[
        i, 'name'] == 'PLANT-HOUSE' or df.loc[i, 'name'] == 'GARDEN FRAME':

        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/greenhouse.png')

    elif df.loc[i, 'name'] == 'SILO' or df.loc[i, 'name'] == 'GRAIN SILO':

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/silo.png')


    elif df.loc[i, 'name'] == 'STADIUM':

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/stadium.png')


    elif 'HOOK BARRIER' in df.loc[i, 'name']:

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/hook.png')


    elif 'NET BARRIER' in df.loc[i, 'name']:

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/net.png')


    elif df.loc[i, 'name'] == 'CONCRETE BARRIER' or df.loc[i, 'name'] == 'CONCRETE BLOCK' or df.loc[
        i, 'name'] == 'BETON BARIYER':

        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/concrete_barrier.png')


    elif 'WALL' in df.loc[i, 'name']:

        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/wall.png')


    elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/nf_antenna.png')


    elif (df.loc[i, 'name'] == 'DVOR' or df.loc[i, 'name'] == 'DVOR_LC' or df.loc[i, 'name'] == 'DVOR_MONITOR'
          or df.loc[i, 'name'] == 'FFM_18' or df.loc[i, 'name'] == 'FFM_17L' or df.loc[i, 'name'] == 'FFM-35R'
          or df.loc[i, 'name'] == "FFM_34L" or df.loc[i, 'name'] == 'FFM_36' or df.loc[
              i, 'name'] == 'GLIDE PATH'
          or df.loc[i, 'name'] == 'GLIDEPAT CON.' or df.loc[i, 'name'] == 'GLIDE PATH SHELTER' or df.loc[
              i, 'name'] == 'GLIDE PATH CONTAINER'
          or df.loc[i, 'name'] == 'GP' or df.loc[i, 'name'] == 'GP CABIN' or df.loc[i, 'name'] == 'GP STATION'
          or df.loc[i, 'name'] == 'GP_16R_MONITOR' or df.loc[i, 'name'] == 'GP/NAVAID' or df.loc[
              i, 'name'] == 'GP/DME'
          or df.loc[i, 'name'] == 'GP_16R_OBS_LT' or df.loc[i, 'name'] == 'GP_17L_MONITOR' or df.loc[
              i, 'name'] == 'GP_17L_OBS_LT'
          or df.loc[i, 'name'] == 'GP_34L_MONITOR' or df.loc[i, 'name'] == 'GP_18_OBS_LT' or df.loc[
              i, 'name'] == 'GP_18_MONITOR'
          or df.loc[i, 'name'] == 'GP_34L_OBS_LT' or df.loc[i, 'name'] == 'GP_35R_MONITOR' or df.loc[
              i, 'name'] == 'GP_35R_OBS_LT'
          or df.loc[i, 'name'] == 'LLZ CON.' or df.loc[i, 'name'] == 'GP_36_OBS_LT' or df.loc[
              i, 'name'] == 'GP_36_MONITOR'
          or df.loc[i, 'name'] == 'LLZ CONTAINER' or df.loc[i, 'name'] == 'LLZ16' or df.loc[
              i, 'name'] == 'LLZ_18'
          or df.loc[i, 'name'] == 'RVR' or df.loc[i, 'name'] == 'PAPI_COVER' or df.loc[
              i, 'name'] == 'LOCALIZER' or
          df.loc[i, 'name'] == 'RAPCON'
          or df.loc[i, 'name'] == 'RVR-SENSOR') or df.loc[i, 'name'] == 'NDB FIELD' or df.loc[
        i, 'name'] == 'GCA' or \
            df.loc[i, 'name'] == 'SENTRY BOX' \
            or df.loc[i, 'name'] == 'NFM_34L':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/other_navigation_aid.png')

    elif df.loc[i, 'name'] == 'GSM BASE STATION' or df.loc[i, 'name'] == 'GSM STATION':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/gsm_anten.png')


    elif df.loc[i, 'name'] == 'GAS STATION':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/gas-station.png')


    elif df.loc[i, 'name'] == 'RADAR_STATION':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/radar.png')


    elif (df.loc[i, 'name'] == 'CABIN' or df.loc[i, 'name'] == 'CONSTRUCTION' or df.loc[i, 'name'] == 'COTTAGE'
          or df.loc[i, 'name'] == 'GUARD COTTAGE' or df.loc[i, 'name'] == 'STRUCTURE'):
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/cabin.png')


    elif df.loc[i, 'name'] == 'HANGAR':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/hangar.png')


    elif df.loc[i, 'name'] == 'MILITARY TRENCH':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/trench.png')


    elif df.loc[i, 'name'] == 'REFLECTOR':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/reflector.png')


    elif df.loc[i, 'name'] == 'ROCK' or df.loc[i, 'name'] == 'STACK' \
            or df.loc[i, 'name'] == 'CLIFF':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/rock_stack_cliff.png')


    elif df.loc[i, 'name'] == 'TREE':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/tree.png')


    elif df.loc[i, 'name'] == 'VAN CASTLE':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/castle.png')


    elif df.loc[i, 'name'] == 'BRIDGE_DECK':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/bridge_deck.png')


    elif df.loc[i, 'name'] == 'TRANSFORMER':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/transformer.png')


    elif df.loc[i, 'name'] == 'TRAFFIC_SIGN' or df.loc[i, 'name'] == 'TRAFFIC BOARD' \
            or df.loc[i, 'name'] == 'SIGNBOARD':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/sign_board.png')


    elif df.loc[i, 'name'] == 'PYLON':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/pylon.png')


    elif df.loc[i, 'name'] == 'CRANE':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/crane.png')


    elif df.loc[i, 'name'] == 'ARFF POOL':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/arff_pool.png')


    elif df.loc[i, 'name'] == 'ENERGY TRANSMISSION LINE' or df.loc[i, 'name'] == 'POWER_TRANSMISSION_LINE':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/transmission.png')

    elif df.loc[i, 'name'] == 'CONTAINER':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/container.png')


    elif 'TERRAIN' in df.loc[i, 'name']:
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/terrain.png')


    elif df.loc[i, 'name'] == 'BASE STATION':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/base_station.png')


    elif df.loc[i, 'name'] == 'BILLBOARD':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/billboard.png')


    elif df.loc[i, 'name'] == 'CAMERA PANEL':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/panel.png')


    elif df.loc[i, 'name'] == 'FENCE' or df.loc[i, 'name'] == 'WIRE FENCE':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/fence.png')


    elif df.loc[i, 'name'] == 'FUEL_TANK':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/fuel_tank.png')


    elif df.loc[i, 'name'] == 'WATER TANK':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/water_tank.png')


    elif df.loc[i, 'name'] == 'WATER ROSERVOIR':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/reservoir.png')


    elif df.loc[i, 'name'] == 'ENERGY CABIN':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/energy_cabin.png')


    elif df.loc[i, 'name'] == 'METEOROLOGY DEVICE':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/meteo_device.png')


    elif df.loc[i, 'name'] == 'OKIS':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/okis.png')


    elif df.loc[i, 'name'] == 'TERMINAL':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/terminal.png')


    elif df.loc[i, 'name'] == 'VOICE BIRD SCARING SYSTEM':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/vbss.png')


    elif df.loc[i, 'name'] == 'WATCH BOX':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/watch_box.png')


    elif df.loc[i, 'name'] == 'GNSS_MEASUREMENT_POINT':
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/gnss.png')

    elif df.loc[i, 'name'] == 'OTHER':
        icons = folium.CustomIcon(
            icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/other_navigation_aid.png')

    else:
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/laughing.png')

    return icons

if __name__ == '__main__':
    app.run(debug=True, port=5001)
