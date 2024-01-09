import os
import folium
import geopandas
import pandas as pd
from shapely import wkt
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import gunicorn
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
import logging
from flask_cors import cross_origin

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
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy()
migrate = Migrate()
db.init_app(app)
migrate.init_app(app, db)


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


# with app.app_context():
#     db.create_all()

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
    '''This is another implementation for ltfe obstacles to get coordinates in appropriate format.'''
    n = max(1, n)
    coordinate_list = []
    for i in range(0, len(xs), n):
        coordinate_list.append(xs[i:i + n])
    for t in coordinate_list:
        ind = coordinate_list.index(t)
        coordinate_list[ind] = [float(t[1]), float(t[0])]
    return coordinate_list


@app.route('/get_all', methods=['GET'])
@cross_origin()
def get_all():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    point = []
    polylines = []
    polygons = []
    sql_ad = f'''SELECT geo,coordinate,elevation,type FROM ad_obstacles'''
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    df = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')

    for q in range(df.shape[0]):
        coor = df.loc[q, 'coordinate'].replace(',', '.').split(' ')
        popup = (f"Elevation: {df.loc[q, 'elevation']} FT Type: {df.loc[q, 'type']} "
                 f"Coordinates: {coor[1]}N, {coor[0]}E")

        point.append({'lat': float(coor[1]), 'lon': float(coor[0]), 'popup': popup})

    sql_enr = f'''SELECT geo,coordinate,elevation,type FROM enr_obstacles'''
    df_enr = pd.read_sql(sql_enr, con=engine)
    df_enr['geometry'] = df_enr['geo'].apply(wkt.loads)
    df_enr = geopandas.GeoDataFrame(df_enr, crs='EPSG:4326')

    for w in range(df_enr.shape[0]):
        coor = df_enr.loc[w, 'geometry']
        popup = (f"Elevation: {df_enr.loc[w, 'elevation']} FT Type: {df_enr.loc[w, 'type']} "
                 f"Coordinates: {coor.y}N, {coor.x}E")

        point.append({'lat': float(coor.y), 'lon': float(coor.x), 'popup': popup})

    sql_a2 = f'''SELECT geo,coordinate,elevation, obstacle_type, aerodrome FROM area2a_obstacles'''
    df_a2 = pd.read_sql(sql_a2, con=engine)
    df_a2['geometry'] = df_a2['geo'].apply(wkt.loads)
    wdf = geopandas.GeoDataFrame(df_a2, crs='EPSG:4326')
    for i in range(wdf.shape[0]):
        coor = wdf.get_coordinates(ignore_index=True)
        if wdf.loc[i, 'geometry'].geom_type == 'Point':
            hh = wdf.loc[i, 'coordinate'].replace(',', '.').split(' ')
            popup = (f"Elevation: {wdf.loc[i, 'elevation']} FT Type: {wdf.loc[i, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[i, 'y']}N, {coor.loc[i, 'x']}E")
            point.append({'lat': float(hh[0]), 'lon': float(hh[1]), 'popup': popup})

        elif wdf.loc[i, 'geometry'].geom_type == 'MultiLineString':
            if wdf.loc[i, 'aerodrome'] == 'ltfe_Area2a_Obstacles':
                polylines.append({'latlngs': chunks3(wdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {wdf.loc[i, 'elevation']} FT  Type: {wdf.loc[i, 'obstacle_type']} Coordinates(..N..E): {chunks3(wdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}"})
            elif wdf.loc[i, 'aerodrome'] != 'ltfe_Area2a_Obstacles':
                polylines.append({'latlngs': chunks2(wdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {wdf.loc[i, 'elevation']} FT  Type: {wdf.loc[i, 'obstacle_type']} Coordinates(..N..E): {chunks2(wdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}"})
        elif wdf.loc[i, 'geometry'].geom_type == 'MultiPolygon':
            polygons.append({'latlngs': chunks2(wdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                             'popup': f"Elevation: {wdf.loc[i, 'elevation']} FT  Type: {wdf.loc[i, 'obstacle_type']}  Coordinates(..N..E): {chunks2(wdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}"})

    sql_ltac = "SELECT geo,Elevation,Obstacle_Type,Coordinate FROM ltac_area3_obstacles"
    df_ltac = pd.read_sql(sql_ltac, con=engine)
    df_ltac['geometry'] = df_ltac['geo'].apply(wkt.loads)
    ltac = geopandas.GeoDataFrame(df_ltac, crs='EPSG:4326')
    for e in range(ltac.shape[0]):
        coor = ltac.get_coordinates(ignore_index=True)
        if ltac.loc[e, 'geometry'].geom_type == 'Point':
            popup = (f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}"
                     f" Coordinates: {coor.loc[e, 'x']}N, {coor.loc[e, 'y']}E")

            point.append({'lat': coor.loc[e, 'x'], 'lon': coor.loc[e, 'y'], 'popup': popup})

        elif ltac.loc[e, 'geometry'].geom_type == 'LineString':
            polylines.append({'latlngs': chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                              'popup': f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}  Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}"})

        elif ltac.loc[e, 'geometry'].geom_type == 'Polygon':
            polygons.append({'latlngs': chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                             'popup': f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}  Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}"})

    sql_a3 = f'''SELECT geo,elevation,coordinate,obstacle_type FROM area3_obstacles'''
    df_a3 = pd.read_sql(sql_a3, con=engine)
    df_a3['geometry'] = df_a3['geo'].apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df_a3, crs='EPSG:4326')
    for t in range(gdf.shape[0]):

        coor = gdf.get_coordinates(ignore_index=True)
        # icons = folium.CustomIcon(icon_image='/app/static/assets/images/marker_dot.png')
        if gdf.loc[t, 'geometry'].geom_type == 'Point':
            coordddd = gdf.loc[t, 'coordinate'].replace(',', '.').split(' ')
            popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[t, 'y']}N, {coor.loc[t, 'x']}E")

            point.append({'lat': coordddd[0], 'lon': coordddd[1], 'popup': popup})


        elif gdf.loc[t, 'geometry'].geom_type == 'MultiLineString':
            folium.PolyLine(locations=chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
                            color='purple',
                            popup=f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                                  f" Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}")
            polylines.append({'latlngs': chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
                              'popup': f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']}  Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}"})

    sql_fm = "SELECT geo,coordinate,elevation,type FROM ltfm_area4_obstacles"
    df_fm = pd.read_sql(sql_fm, con=engine)
    df_fm['geometry'] = df_fm['geo'].apply(wkt.loads)
    xdf = geopandas.GeoDataFrame(df_fm, crs='EPSG:4326')
    for u in range(xdf.shape[0]):
        coor = xdf.get_coordinates(ignore_index=True)
        if xdf.loc[u, 'geometry'].geom_type == 'Point':
            popup = (f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}"
                     f" Coordinates: {coor.loc[u, 'y']}N, {coor.loc[u, 'x']}E")

            point.append({'lat': coor.loc[u, 'y'], 'lon': coor.loc[u, 'x'], 'popup': popup})

        elif xdf.loc[u, 'geometry'].geom_type == 'MultiLineString':
            polylines.append({'latlngs': chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
                              'popup': f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}  Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}"})

        elif xdf.loc[u, 'geometry'].geom_type == 'MultiPolygon':
            polygons.append({'latlngs': chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
                             'popup': f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}  Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}"})

    sql_a4 = f'''SELECT geo,coordinate,elevation,obstacle_type,obstacle_identifier,aerodrome FROM area4_obstacles'''
    df_a4 = pd.read_sql(sql_a4, con=engine)
    df_a4['geometry'] = df_a4['geo'].apply(wkt.loads)
    hdf = geopandas.GeoDataFrame(df_a4, crs='EPSG:4326')
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

            if hdf.loc[l, 'aerodrome'] == 'ltfe_area_4_area_4_28r_area_4_28r_Area4_Obstacles' or hdf.loc[
                l, 'aerodrome'] == 'ltfe_area_4_area_4_10l_area_4_10l_Area4_Obstacles':
                polylines.append({'latlngs': chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})
            else:
                polylines.append({'latlngs': chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})



        elif hdf.loc[l, 'geometry'].geom_type == 'MultiPolygon':
            if len(hdf.loc[l, 'coordinate']) % 2 != 0:
                hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]

            if hdf.loc[l, 'aerodrome'] == 'ltfe_area_4_area_4_28r_area_4_28r_Area4_Obstacles':
                polygons.append({'latlngs': chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                 'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})
            else:

                polygons.append({'latlngs': chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                 'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})

        elif hdf.loc[l, 'geometry'].geom_type == 'Point':

            coor = hdf.loc[l, 'coordinate'].replace(',', '.').split(' ')

            popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                     f" Coordinates: {coor[0]}N, {coor[1]}E")
            point.append({'lat': coor[0], 'lon': coor[1], 'popup': popup})

    return jsonify({'points': point, 'polylines': polylines, 'polygons': polygons})


@app.route('/all', methods=['GET', 'POST'])
def all():
    return render_template('mapping.html', title='All Obstacles | Folium')


@app.route('/marker_c', methods=['GET'])
@cross_origin()
def marker_c():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    markerz = []
    pathz = []
    sql_ad = f'''SELECT geo, coordinate, elevation, type, name FROM ad_obstacles'''

    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    df = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')

    for i in range(df.shape[0]):
        if df.loc[i, 'type'] == 'TREE':
            path = '/static/assets/images/tree.png'

        elif df.loc[i, 'type'] == 'POLE':
            path = '/static/assets/images/pole.png'

        elif df.loc[i, 'type'] == 'BUILDING':
            path = '/static/assets/images/building.png'


        elif df.loc[i, 'type'] == 'TRANSMISSION LINE':
            path = '/static/assets/images/transmission.png'

        elif df.loc[i, 'type'] == 'CRANE':
            path = '/static/assets/images/tower_crane.png'

        elif df.loc[i, 'type'] == 'ANTENNA':
            path = '/static/assets/images/antenna.png'

        elif df.loc[i, 'type'] == 'TOWER':
            path = '/static/assets/images/tower-block.png'

        elif df.loc[i, 'type'] == 'WALL':
            path = '/static/assets/images/wall.png'

        elif df.loc[i, 'type'] == 'OTHER':
            path = '/static/assets/images/other_obs.png'

        elif df.loc[i, 'type'] == 'NATURAL_HIGHPOINT':
            path = '/static/assets/images/rock_stack_cliff.png'


        elif df.loc[i, 'type'] == 'FENCE':
            path = '/static/assets/images/fence.png'


        elif df.loc[i, 'type'] == 'FUEL_SYSTEM':
            path = '/static/assets/images/fuel_tank.png'


        elif df.loc[i, 'type'] == 'WATER_TOWER':
            path = '/static/assets/images/water_tank.png'



        elif df.loc[i, 'type'] == 'GENERAL_UTILITY':
            path = '/static/assets/images/energy_cabin.png'

        elif df.loc[i, 'type'] == 'NAVAID':
            path = '/static/assets/images/other_navigation_aid.png'

        elif df.loc[i, 'type'] == 'SIGN':
            path = '/static/assets/images/sign_board.png'

        elif df.loc[i, 'type'] == 'STACK':
            path = '/static/assets/images/reservoir.png'

        elif df.loc[i, 'type'] == 'TANK':
            path = '/static/assets/images/fuel_tank.png'

        elif df.loc[i, 'type'] == 'WINDMILL':
            path = '/static/assets/images/wind-turbine.png'

        else:
            path = '/static/assets/images/laughing.png'

        coor = df.loc[i, 'coordinate'].replace(',', '.').split(' ')
        popup = (f"Elevation: {df.loc[i, 'elevation']} FT Type: {df.loc[i, 'type']} "
                 f"Coordinates: {coor[1]}N, {coor[0]}E")
        markerz.append({'lat': float(coor[1]), 'lon': float(coor[0]), 'popup': popup})
        pathz.append({'path': path})

    return jsonify({'markers': markerz, 'paths': pathz})


logging.basicConfig(level=logging.DEBUG)  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)


@app.route("/", methods=['GET', 'POST'])
def fullscreen():
    return render_template('aerodrome.html', title='Fullscreen AD Map | Folium')


@app.route("/get_markers", methods=['GET'])
@cross_origin()
def get_markers():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    markerz = []

    sql_ad = f'''SELECT geo,coordinate,elevation,type FROM ad_obstacles'''
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    df = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')

    for i in range(df.shape[0]):
        coor = df.loc[i, 'coordinate'].replace(',', '.').split(' ')
        popup = (f"Elevation: {df.loc[i, 'elevation']} FT Type: {df.loc[i, 'type']} "
                 f"Coordinates: {coor[1]}N, {coor[0]}E")

        markerz.append({'lat': float(coor[1]), 'lon': float(coor[0]), 'popup': popup})

    return jsonify({'markers': markerz})


@app.route("/aerodrome", methods=['GET', 'POST'])
def ad():
    return render_template('ad.html', title=' AD Map | Folium')


@app.route("/get_enr", methods=['GET'])
@cross_origin()
def get_enr():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    markerz = []

    sql_ad = f'''SELECT geo,coordinate,elevation,type FROM enr_obstacles'''
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    df = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')

    for i in range(df.shape[0]):
        coor = df.loc[i, 'geometry']
        popup = (f"Elevation: {df.loc[i, 'elevation']} FT Type: {df.loc[i, 'type']} "
                 f"Coordinates: {coor.y}N, {coor.x}E")

        markerz.append({'lat': float(coor.y), 'lon': float(coor.x), 'popup': popup})

    return jsonify({'markers': markerz})


@app.route("/enrobs", methods=['GET', 'POST'])
def enr_obstacles():
    return render_template('enr.html', title='ENR Obstacles | Folium')


@app.route("/get_area2a", methods=['GET'])
@cross_origin()
def get_area2a():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    sql_ad = f'''SELECT geo,coordinate,elevation, obstacle_type, aerodrome FROM area2a_obstacles'''
    df_ad = pd.read_sql(sql_ad, con=engine)
    df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
    point = []
    polylines = []
    polygons = []
    for i in range(gdf.shape[0]):
        coor = gdf.get_coordinates(ignore_index=True)
        if gdf.loc[i, 'geometry'].geom_type == 'Point':
            hh = gdf.loc[i, 'coordinate'].replace(',', '.').split(' ')
            popup = (f"Elevation: {gdf.loc[i, 'elevation']} FT Type: {gdf.loc[i, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[i, 'y']}N, {coor.loc[i, 'x']}E")
            point.append({'lat': float(hh[0]), 'lon': float(hh[1]), 'popup': popup})

        elif gdf.loc[i, 'geometry'].geom_type == 'MultiLineString':
            if gdf.loc[i, 'aerodrome'] == 'ltfe_Area2a_Obstacles':
                polylines.append({'latlngs': chunks3(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} Coordinates(..N..E): {chunks3(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}"})
            else:
                polylines.append({'latlngs': chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} Coordinates(..N..E): {chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}"})
        elif gdf.loc[i, 'geometry'].geom_type == 'MultiPolygon':
            polygons.append({'latlngs': chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
                             'popup': f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']}  Coordinates(..N..E): {chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}"})
    return jsonify({'points': point, 'polylines': polylines, 'polygons': polygons})


@app.route('/area2a', methods=['GET', 'POST'])
def area_2a_obstacles():
    return render_template('area2a.html', title='Area 2A Obstacles | Folium')


@app.route("/get_area3", methods=['GET'])
@cross_origin()
def get_area3():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    point = []
    polylines = []
    polygons = []
    sql_ltac = "SELECT geo,Elevation,Obstacle_Type,Coordinate FROM ltac_area3_obstacles"
    df_ltac = pd.read_sql(sql_ltac, con=engine)
    df_ltac['geometry'] = df_ltac['geo'].apply(wkt.loads)
    ltac = geopandas.GeoDataFrame(df_ltac, crs='EPSG:4326')
    for e in range(ltac.shape[0]):
        coor = ltac.get_coordinates(ignore_index=True)
        if ltac.loc[e, 'geometry'].geom_type == 'Point':
            popup = (f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}"
                     f" Coordinates: {coor.loc[e, 'x']}N, {coor.loc[e, 'y']}E")

            point.append({'lat': coor.loc[e, 'x'], 'lon': coor.loc[e, 'y'], 'popup': popup})

        elif ltac.loc[e, 'geometry'].geom_type == 'LineString':
            polylines.append({'latlngs': chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                              'popup': f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}  Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}"})

        elif ltac.loc[e, 'geometry'].geom_type == 'Polygon':
            polygons.append({'latlngs': chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
                             'popup': f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}  Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}"})

    sql_a3 = f'''SELECT geo,elevation,coordinate,obstacle_type FROM area3_obstacles'''
    df_a3 = pd.read_sql(sql_a3, con=engine)
    df_a3['geometry'] = df_a3['geo'].apply(wkt.loads)
    gdf = geopandas.GeoDataFrame(df_a3, crs='EPSG:4326')
    for t in range(gdf.shape[0]):
        coor = gdf.get_coordinates(ignore_index=True)
        if gdf.loc[t, 'geometry'].geom_type == 'Point':
            coordddd = gdf.loc[t, 'coordinate'].replace(',', '.').split(' ')
            popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[t, 'y']}N, {coor.loc[t, 'x']}E")

            point.append({'lat': coordddd[0], 'lon': coordddd[1], 'popup': popup})

        elif gdf.loc[t, 'geometry'].geom_type == 'MultiLineString':
            polylines.append({'latlngs': chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
                              'popup': f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']}  Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}"})

    return jsonify({'points': point, 'polylines': polylines, 'polygons': polygons})


@app.route('/area3', methods=['GET', 'POST'])
def area_3():
    return render_template('area3.html', title='Area 3 Obstacles | Folium')


@app.route("/get_area4", methods=['GET'])
@cross_origin()
def get_area4():
    engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
    point = []
    polylines = []
    polygons = []
    sql_fm = "SELECT geo,coordinate,elevation,type FROM ltfm_area4_obstacles"
    df_fm = pd.read_sql(sql_fm, con=engine)
    df_fm['geometry'] = df_fm['geo'].apply(wkt.loads)
    xdf = geopandas.GeoDataFrame(df_fm, crs='EPSG:4326')
    for u in range(xdf.shape[0]):
        coor = xdf.get_coordinates(ignore_index=True)
        if xdf.loc[u, 'geometry'].geom_type == 'Point':
            popup = (f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}"
                     f" Coordinates: {coor.loc[u, 'y']}N, {coor.loc[u, 'x']}E")

            point.append({'lat': coor.loc[u, 'y'], 'lon': coor.loc[u, 'x'], 'popup': popup})

        elif xdf.loc[u, 'geometry'].geom_type == 'MultiLineString':
            polylines.append({'latlngs': chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
                              'popup': f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}  Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}"})

        elif xdf.loc[u, 'geometry'].geom_type == 'MultiPolygon':
            polygons.append({'latlngs': chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
                             'popup': f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}  Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}"})

    sql_a4 = f'''SELECT geo,coordinate,elevation,obstacle_type,obstacle_identifier,aerodrome FROM area4_obstacles'''
    df_a4 = pd.read_sql(sql_a4, con=engine)
    df_a4['geometry'] = df_a4['geo'].apply(wkt.loads)
    hdf = geopandas.GeoDataFrame(df_a4, crs='EPSG:4326')
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
                polylines.append({'latlngs': chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})
            else:
                polylines.append({'latlngs': chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                  'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})



        elif hdf.loc[l, 'geometry'].geom_type == 'MultiPolygon':
            if len(hdf.loc[l, 'coordinate']) % 2 != 0:
                hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]

            if hdf.loc[l, 'aerodrome'] == 'ltfe_area_4_area_4_28r_area_4_28r_Area4_Obstacles':
                polygons.append({'latlngs': chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                 'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks3(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})
            else:

                polygons.append({'latlngs': chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
                                 'popup': f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']}  Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}"})

        elif hdf.loc[l, 'geometry'].geom_type == 'Point':

            coor = hdf.loc[l, 'coordinate'].replace(',', '.').split(' ')

            popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                     f" Coordinates: {coor[0]}N, {coor[1]}E")
            point.append({'lat': coor[0], 'lon': coor[1], 'popup': popup})

    return jsonify({'points': point, 'polylines': polylines, 'polygons': polygons})


@app.route('/area4')
def area_4():
    return render_template('area4.html', title='Area 4 Obstacles | Folium')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
