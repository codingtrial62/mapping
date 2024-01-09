import folium
import shapely
from flask import Flask, render_template
import os
import pandas as pd
import geopandas
from folium.plugins import FastMarkerCluster
from pathlib import Path
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float
import shapely as shp
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from shapely import wkt

secret_key = os.environ.get('SECRET_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db'
db = SQLAlchemy()
db.init_app(app)

path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_to_enr = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles').rglob("*.xml"))
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))


# def read_area_3_4_db(path_list, area: int):
#     """
#     This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
#     LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
#     WGS84. Also caution for file paths especially having space in it. Sometimes manually changing file names may be better:).
#
#     """
#     if area == 3:
#         layer_name = str(path_list[0])[69:].replace('/', '_').replace('.gdb', '').lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area3_obstacles.db', echo=False)
#         gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         for i in path_list[1:]:
#             layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
#             bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#             gdf = pd.concat([gdf, bdf], ignore_index=True)
#
#     elif area == 4:
#         layer_name = str(path_list[0])[69:].replace('/', '_').replace('.gdb', '').lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#         gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         for j in path_list[1:]:
#             layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
#             bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#             gdf = pd.concat([gdf, bdf], ignore_index=True)
#
#     else:
#         print('Wrong area number. Please enter 3 or 4.')
#     return gdf
#
#
# def read_ltfm_area_4_xml(path_list_xml):
#     layer_name = str(path_list_xml[0])[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#     engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#     xdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#     for k in path_list_xml[1:]:
#         layer_name = str(k)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#         ydf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         xdf = pd.concat([xdf, ydf], ignore_index=True)
#     return xdf
#
#
# def read_area2a():
#     path_list = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
#     layer_name = str(path_list[0])[61:].replace('/', '_').replace('.gdb', '').lower()
#     engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area2a_obstacles.db', echo=False)
#     gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#
#     for i in path_list[1:]:
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area2a_obstacles.db', echo=False)
#         layer_name = str(i)[61:].replace('/', '_').replace('.gdb', '').lower()
#         bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         gdf = pd.concat([gdf, bdf], ignore_index=True)
#
#     return gdf
#
#
# def read_enr_obs_db(db_path):
#     gdf = geopandas.read_file(db_path)
#     return gdf
#
#
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


# def read_ltac_area3():
#     engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=True)
#
#     point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)
#
#     for i in range(point_df.shape[0]):
#         point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
#                                                 float(point_df.loc[i, 'Coordinate'].split(' ')[1]))
#
#     line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
#     for i in range(line_df.shape[0]):
#         line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))
#
#     pointline = pd.concat([point_df, line_df], ignore_index=True)
#
#     polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)
#     for i in range(polygon_df.shape[0]):
#
#         if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
#             polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
#             polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
#         else:
#             polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))
#     poly_point_line = pd.concat([polygon_df, pointline], ignore_index=True)
#     return poly_point_line
#
#
# ltac = read_ltac_area3()
# ltac_gdf = geopandas.GeoDataFrame(ltac, geometry='GEOMETRY')

# engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db', echo=False)
# for j in path_list_area_4:
#     layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
#     hdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#     for l in range(hdf.shape[0]):
#         if len(hdf.loc[l,'coordinate'])%2 != 0:
#             hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]


#


# def read_ad_obs(path_to_ad):
#     layer_name = str(path_list_ad[1])[64:78].lower()
#     engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db', echo=False)
#     gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#     for p in path_list_ad[2:]:
#         layer_name = str(p)[64:78].lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db', echo=False)
#         cdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         gdf = pd.concat([gdf, cdf], ignore_index=True)
#
#     return gdf


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
    sequencenumber = db.Column(db.Integer())
    correctionnumber = db.Column(db.Integer())
    timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
    name = db.Column(db.String())
    type = db.Column(db.String())
    lighted = db.Column(db.String())
    group = db.Column(db.String())
    verticalextent = db.Column(db.Integer())
    verticalextent_uom = db.Column(db.String())
    timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
    designator = db.Column(db.String())
    elevation = db.Column(db.String())
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


#
# for p in path_list_ad[:]:
#     ad_df = geopandas.read_file(p)
#     table = str(p)[64:68].lower()
#     coord_list = []
#     coords = ad_df.get_coordinates()
#     for i in range(ad_df.shape[0]):
#         ad_df['aerodrome'] = table
#         coord_list.append([float(coords.loc[i].x), float(coords.loc[i].y)])
#         try:
#             with app.app_context():
#
#                 new = AerodromeObstacles(aerodrome=ad_df.loc[i, 'aerodrome'],
#                                          coordinate=f"{coord_list[i][0]} {coord_list[i][1]}",
#                                          gml_id=ad_df.loc[i, 'gml_id'],
#                                          identifier=ad_df.loc[i, 'identifier'],
#                                          beginposition=ad_df.loc[i, 'beginPosition'],
#                                          interpretation=ad_df.loc[i, 'interpretation'],
#                                          sequencenumber=ad_df.loc[i, 'sequenceNumber'],
#                                          correctionnumber=ad_df.loc[i, 'correctionNumber'],
#                                          timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                          ad_df.loc[
#                                              i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
#                                          name=ad_df.loc[i, 'name'], type=ad_df.loc[i, 'type'],
#                                          lighted=ad_df.loc[i, 'lighted'],
#                                          group=ad_df.loc[i, 'group'], verticalextent=ad_df.loc[i, 'verticalExtent'],
#                                          verticalextent_uom=ad_df.loc[i, 'verticalExtent_uom'],
#                                          timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ad_df.loc[
#                                              i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
#                                          designator=ad_df.loc[i, 'designator'], elevation=ad_df.loc[i, 'elevation'],
#                                          elevation_uom=ad_df.loc[i, 'elevation_uom'], colour=ad_df.loc[i, 'colour'],
#                                          geo= str(ad_df.loc[i, 'geometry']))
#
#                 db.session.add(new)
#                 db.session.commit()
#
#         except KeyError:
#             ad_df.loc[i, 'colour'] = 'NULL'
#             with app.app_context():
#                 new = AerodromeObstacles(aerodrome=ad_df.loc[i, 'aerodrome'],
#                                          coordinate=f"{coord_list[i][0]} {coord_list[i][1]}",
#                                          gml_id=ad_df.loc[i, 'gml_id'],
#                                          identifier=ad_df.loc[i, 'identifier'],
#                                          beginposition=ad_df.loc[i, 'beginPosition'],
#                                          interpretation=ad_df.loc[i, 'interpretation'],
#                                          sequencenumber=ad_df.loc[i, 'sequenceNumber'],
#                                          correctionnumber=ad_df.loc[i, 'correctionNumber'],
#                                          timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                          ad_df.loc[
#                                              i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
#                                          name=ad_df.loc[i, 'name'], type=ad_df.loc[i, 'type'],
#                                          lighted=ad_df.loc[i, 'lighted'],
#                                          group=ad_df.loc[i, 'group'], verticalextent=ad_df.loc[i, 'verticalExtent'],
#                                          verticalextent_uom=ad_df.loc[i, 'verticalExtent_uom'],
#                                          timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ad_df.loc[
#                                              i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
#                                          designator=ad_df.loc[i, 'designator'], elevation=ad_df.loc[i, 'elevation'],
#                                          elevation_uom=ad_df.loc[i, 'elevation_uom'], colour=ad_df.loc[i, 'colour'],
#                                          geo= str(ad_df.loc[i, 'geometry']))
#                 db.session.add(new)
#                 db.session.commit()
#
#
# for r in path_to_enr[1:]:
#     table = str(r)[65:68] + str(r)[73:82]
#     enr_df = geopandas.read_file(r)
#     enr_coords = enr_df.get_coordinates()
#     coord_list_enr = []
#     for i in range(enr_df.shape[0]):
#         coord_list_enr.append([float(enr_coords.loc[i].x), float(enr_coords.loc[i].y)])
#         with app.app_context():
#             enr_obstacles = EnrouteObstacles(coordinate=f"{coord_list_enr[i][0]} {coord_list_enr[i][1]}",
#                                              gml_id=enr_df.loc[i, 'gml_id'],
#                                              identifier=enr_df.loc[i, 'identifier'],
#                                              beginposition=enr_df.loc[i, 'beginPosition'],
#                                              interpretation=enr_df.loc[i, 'interpretation'],
#                                              sequencenumber=enr_df.loc[i, 'sequenceNumber'],
#                                              correctionnumber=enr_df.loc[i, 'correctionNumber'],
#                                              timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                              enr_df.loc[
#                                                  i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
#                                              name=enr_df.loc[i, 'name'],
#                                              type=enr_df.loc[i, 'type'],
#                                              lighted=enr_df.loc[i, 'lighted'],
#                                              group=enr_df.loc[i, 'group'],
#                                              verticalextent=enr_df.loc[i, 'verticalExtent'],
#                                              verticalextent_uom=enr_df.loc[i, 'verticalExtent_uom'],
#                                              timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=enr_df.loc[
#                                                  i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
#                                              designator=enr_df.loc[i, 'designator'],
#                                              elevation=str(enr_df.loc[i, 'elevation']),
#                                              elevation_uom=enr_df.loc[i, 'elevation_uom'],
#                                              colour=enr_df.loc[i, 'colour'],
#                                              geo=str(enr_df.loc[i, 'geometry']))
#             db.session.add(enr_obstacles)
#             db.session.commit()

#
# for s in path_list_area_2:
#     table = str(s)[61:65].replace('/', '_').replace('.gdb', '').lower() + "_Area2a_Obstacles"
#     area_2a = geopandas.read_file(s, driver='OpenFileGDB')
#     if area_2a.crs != 'EPSG:4326':
#         area_2a = area_2a.to_crs('EPSG:4326')
#
#     print(area_2a.columns)
#     if 'Coordinate' not in area_2a.columns:
#         area_2a.rename(columns={'Coordinates': 'Coordinate'}, inplace=True)
#
#     for i in range(area_2a.shape[0]):
#         if 'Shape_Length' not in area_2a.columns:
#             area_2a.loc[i, 'Shape_Length'] = 0.0
#         with app.app_context():
#             area2a_obstacles = Area2aObstacles(aerodrome=table,
#                                                obstacle_identifier=area_2a.loc[i, 'Obstacle_Identifier'],
#                                                horizontal_accuracy=area_2a.loc[i, 'Horizontal_Accuracy'],
#                                                horizontal_confidence_level=area_2a.loc[
#                                                    i, 'Horizontal_Confidence_Level'],
#                                                elevation=area_2a.loc[i, 'Elevation'],
#                                                height=area_2a.loc[i, 'Height'],
#                                                vertical_accuracy=area_2a.loc[i, 'Vertical_Accuracy'],
#                                                vertical_confidence_level=area_2a.loc[
#                                                    i, 'Vertical_Confidence_Level'],
#                                                obstacle_type=area_2a.loc[i, 'Obstacle_Type'],
#                                                integrity=area_2a.loc[i, 'Integrity'],
#                                                date_and_time_stamp=str(area_2a.loc[i, 'Date_And_Time_Stamp']),
#                                                operations=area_2a.loc[i, 'Operations'],
#                                                effectivity=area_2a.loc[i, 'Effectivity'],
#                                                lighting=area_2a.loc[i, 'Lighting'],
#                                                marking=area_2a.loc[i, 'Marking'],
#                                                horizontal_extent=area_2a.loc[i, 'Horizontal_Extent'],
#                                                obstacle_name=area_2a.loc[i, 'Obstacle_Name'],
#                                                marking_details=area_2a.loc[i, 'Marking_Details'],
#                                                lighting_color=area_2a.loc[i, 'Lighting_Color'],
#                                                coordinate=area_2a.loc[i, 'Coordinate'],
#                                                shape_length=area_2a.loc[i, 'Shape_Length'],
#                                                geo=str(area_2a.loc[i, 'geometry']))
#
#             db.session.add(area2a_obstacles)
#             db.session.commit()
#
# for t in path_list_area_3:
#     table = str(t)[69:73].replace('/', '_').replace('.gdb', '').lower() + "_Area3_Obstacles"
#     area_3_df = geopandas.read_file(t, driver='OpenFileGDB')
#     if area_3_df.crs != 'EPSG:4326':
#         area_3_df = area_3_df.to_crs('EPSG:4326')
#
#
#
#     for i in range(area_3_df.shape[0]):
#         if 'Shape_Length' not in area_3_df.columns:
#             area_3_df.loc[i, 'Shape_Length'] = 0.0
#         with app.app_context():
#             area3_obstacles = Area3Obstacles(aerodrome=table,
#                                              obstacle_identifier=area_3_df.loc[i, 'Obstacle_Identifier'],
#                                              horizontal_accuracy=area_3_df.loc[i, 'Horizontal_Accuracy'],
#                                              horizontal_confidence_level=area_3_df.loc[
#                                                  i, 'Horizontal_Confidence_Level'],
#                                              elevation=area_3_df.loc[i, 'Elevation'],
#                                              height=area_3_df.loc[i, 'Height'],
#                                              vertical_accuracy=area_3_df.loc[i, 'Vertical_Accuracy'],
#                                              vertical_confidence_level=area_3_df.loc[
#                                                  i, 'Vertical_Confidence_Level'],
#                                              obstacle_type=area_3_df.loc[i, 'Obstacle_Type'],
#                                              integrity=area_3_df.loc[i, 'Integrity'],
#                                              date_and_time_stamp=str(area_3_df.loc[i, 'Date_And_Time_Stamp']),
#                                              operations=area_3_df.loc[i, 'Operations'],
#                                              effectivity=area_3_df.loc[i, 'Effectivity'],
#                                              lighting=area_3_df.loc[i, 'Lighting'],
#                                              marking=area_3_df.loc[i, 'Marking'],
#                                              horizontal_extent=area_3_df.loc[i, 'Horizontal_Extent'],
#                                              obstacle_name=area_3_df.loc[i, 'Obstacle_Name'],
#                                              marking_details=area_3_df.loc[i, 'Marking_Details'],
#                                              lighting_color=area_3_df.loc[i, 'Lighting_Color'],
#                                              coordinate=area_3_df.loc[i, 'Coordinate'],
#                                              shape_length=area_3_df.loc[i, 'Shape_Length'],
#                                              geo=str(area_3_df.loc[i, 'geometry']))
#
#             db.session.add(area3_obstacles)
#             db.session.commit()
#
# """
# Area 3 LTAC Obstacles are in format of .mdb. To handle that https://fishcodelib.com/index.htm has a tool called
# db.Migration.Net which converts .mdb to .sqlite. Then we can use geopandas to read the .sqlite file."""
# """ Getting data from ltac_obstacles.db which is created from .mdb file. """
# engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=False)
#
# point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)
#
# for i in range(point_df.shape[0]):
#     point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
#                                             float(point_df.loc[i, 'Coordinate'].split(' ')[1]))
#
# point_gdf = geopandas.GeoDataFrame(point_df, geometry='GEOMETRY', crs='EPSG:4326')
#
#
# line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
# for i in range(line_df.shape[0]):
#     line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))
#
# line_gdf = geopandas.GeoDataFrame(line_df, geometry='GEOMETRY', crs='EPSG:4326')
#
# polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)
#
# for i in range(polygon_df.shape[0]):
#
#     if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
#         polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
#         polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
#     else:
#         polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))
#
# polygon_gdf = geopandas.GeoDataFrame(polygon_df, geometry='GEOMETRY', crs='EPSG:4326')
#
#
# ltac_area3 = pd.concat([point_gdf, line_gdf, polygon_gdf], ignore_index=True)
#
#
# """ Getting data from ltac_obstacles.db which is created from .mdb file. """
#
# for w in range(ltac_area3.shape[0]):
#     with app.app_context():
#         ltac_area3_obstacles = LtacArea3Obstacles(Obstacle_Identifier=ltac_area3.loc[w, 'Obstacle_Identifier'],
#                                                   Horizontal_Accuracy=ltac_area3.loc[w, 'Horizontal_Accuracy'],
#                                                   Horizontal_Confidence_Level=ltac_area3.loc[
#                                                       w, 'Horizontal_Confidence_Level'],
#                                                   Elevation=ltac_area3.loc[w, 'Elevation'],
#                                                   Height=ltac_area3.loc[w, 'Height'],
#                                                   Vertical_Accuracy=ltac_area3.loc[w, 'Vertical_Accuracy'],
#                                                   Vertical_Confidence_Level=ltac_area3.loc[
#                                                       w, 'Vertical_Confidence_Level'],
#                                                   Obstacle_Type=ltac_area3.loc[w, 'Obstacle_Type'],
#                                                   Integrity=ltac_area3.loc[w, 'Integrity'],
#                                                   Date_And_Time_Stamp=str(ltac_area3.loc[w, 'Date_And_Time_Stamp']),
#                                                   Operations=ltac_area3.loc[w, 'Operations'],
#                                                   Effectivity=ltac_area3.loc[w, 'Effectivity'],
#                                                   Lighting=ltac_area3.loc[w, 'Lighting'],
#                                                   Marking=ltac_area3.loc[w, 'Marking'],
#                                                   Obstacle_Name=ltac_area3.loc[w, 'Obstacle_Name'],
#                                                   Lighting_Color=ltac_area3.loc[w, 'Lighting_Color'],
#                                                   Marking_Details=ltac_area3.loc[w, 'Marking_Details'],
#                                                   Coordinate=ltac_area3.loc[w, 'Coordinate'],
#                                                   SHAPE_Length=ltac_area3.loc[w, 'SHAPE_Length'],
#                                                   SHAPE_Area=ltac_area3.loc[w, 'SHAPE_Area'],
#                                                   Horizontal_Extent=ltac_area3.loc[w, 'Horizontal_Extent'],
#                                                   geo=str(ltac_area3.loc[w, 'GEOMETRY']))
#
#         db.session.add(ltac_area3_obstacles)
#         db.session.commit()
#
# for u in path_list_area_4:
#     table = str(u)[69:].replace('/', '_').replace('.gdb', '').lower() + "_Area4_Obstacles"
#     area_4_df = geopandas.read_file(u, driver='OpenFileGDB')
#     if area_4_df.crs != 'EPSG:4326':
#         area_4_df = area_4_df.to_crs('EPSG:4326')
#
#
#
#
#     for i in range(area_4_df.shape[0]):
#         if 'Shape_Length' not in area_4_df.columns:
#                      area_4_df.loc[i, 'Shape_Length'] = 0.0
#         if 'Shape_Area' not in area_4_df.columns:
#             area_4_df.loc[i, 'Shape_Area'] = 0.0
#         if 'Horizontal_Extent' not in area_4_df.columns:
#             area_4_df.loc[i, 'Horizontal_Extent'] = 'NULL'
#
#         if 'Coordinate' not in area_4_df.columns:
#             area_4_df.rename(columns={'Coordinates':'Coordinate'}, inplace=True)
#         with app.app_context():
#                 area4_obstacles = Area4Obstacles(aerodrome=table,
#                                                  obstacle_identifier=area_4_df.loc[i, 'Obstacle_Identifier'],
#                                                  horizontal_accuracy=area_4_df.loc[i, 'Horizontal_Accuracy'],
#                                                  horizontal_confidence_level=area_4_df.loc[
#                                                      i, 'Horizontal_Confidence_Level'],
#                                                  elevation=area_4_df.loc[i, 'Elevation'],
#                                                  height=area_4_df.loc[i, 'Height'],
#                                                  vertical_accuracy=area_4_df.loc[i, 'Vertical_Accuracy'],
#                                                  vertical_confidence_level=area_4_df.loc[
#                                                      i, 'Vertical_Confidence_Level'],
#                                                  obstacle_type=area_4_df.loc[i, 'Obstacle_Type'],
#                                                  integrity=area_4_df.loc[i, 'Integrity'],
#                                                  date_and_time_stamp=str(area_4_df.loc[i, 'Date_And_Time_Stamp']),
#                                                  operations=area_4_df.loc[i, 'Operations'],
#                                                  effectivity=area_4_df.loc[i, 'Effectivity'],
#                                                  lighting=area_4_df.loc[i, 'Lighting'],
#                                                  marking=area_4_df.loc[i, 'Marking'],
#                                                  horizontal_extent=area_4_df.loc[i, 'Horizontal_Extent'],
#                                                  obstacle_name=area_4_df.loc[i, 'Obstacle_Name'],
#                                                  marking_details=area_4_df.loc[i, 'Marking_Details'],
#                                                  lighting_color=area_4_df.loc[i, 'Lighting_Color'],
#                                                  coordinate=area_4_df.loc[i, 'Coordinate'],
#                                                  shape_length=area_4_df.loc[i, 'Shape_Length'],
#
#                                                  geo=str(area_4_df.loc[i, 'geometry']))
#
#                 db.session.add(area4_obstacles)
#                 db.session.commit()
#
#
# for j in path_list_area_4_xml:
#
#     ltfm_area4_df = geopandas.read_file(j)
#     if ltfm_area4_df.crs != 'EPSG:4326':
#         ltfm_area4_df = ltfm_area4_df.to_crs('EPSG:4326')
#
#
#
#     coord_list_ltfm = []
#     coords = ltfm_area4_df.get_coordinates()
#     for i in range(ltfm_area4_df.shape[0]):
#         coord_list_ltfm.append([float(coords.loc[i].x), float(coords.loc[i].y)])
#         with app.app_context():
#             ltfm_area4_obstacles = LtfmArea4Obstacles(coordinate=f"{coord_list_ltfm[i][0]} {coord_list_ltfm[i][1]}",
#                                                     gml_id=ltfm_area4_df.loc[i, 'gml_id'],
#                                                     identifier=ltfm_area4_df.loc[i, 'identifier'],
#                                                     beginposition=ltfm_area4_df.loc[i, 'beginPosition'],
#                                                     interpretation=ltfm_area4_df.loc[i, 'interpretation'],
#                                                     sequencenumber=ltfm_area4_df.loc[i, 'sequenceNumber'],
#                                                     correctionnumber=ltfm_area4_df.loc[i, 'correctionNumber'],
#                                                     timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                                       ltfm_area4_df.loc[
#                                                         i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
#                                                     name=ltfm_area4_df.loc[i, 'name'], type=ltfm_area4_df.loc[i, 'type'],
#                                                     lighted=ltfm_area4_df.loc[i, 'lighted'],
#                                                     group=ltfm_area4_df.loc[i, 'group'], verticalextent=ltfm_area4_df.loc[i, 'verticalExtent'],
#                                                     verticalextent_uom=ltfm_area4_df.loc[i, 'verticalExtent_uom'],
#                                                     timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ltfm_area4_df.loc[
#                                                         i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
#                                                     designator=ltfm_area4_df.loc[i, 'designator'], elevation=ltfm_area4_df.loc[i, 'elevation'],
#                                                     elevation_uom=ltfm_area4_df.loc[i, 'elevation_uom'], colour=ltfm_area4_df.loc[i, 'colour'],
#                                                       geo=str(ltfm_area4_df.loc[i, 'geometry']))
#             db.session.add(ltfm_area4_obstacles)
#             db.session.commit()


# @app.route('/', methods=['GET', 'POST'])
# def trial():
#     m = folium.Map(location=[39.925533, 32.866287], zoom_start=6)
#
#     engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db')
#     sql_a4 = "SELECT * FROM area4_obstacles"
#     df_a4 = pd.read_sql(sql_a4, con=engine)
#
#     df_a4['geometry'] = df_a4['geo'].apply(wkt.loads)
#     hdf = geopandas.GeoDataFrame(df_a4, crs='EPSG:4326')
#
#     for j in path_list_area_4:
#         layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower() + "_Area4_Obstacles"
#         fg = folium.FeatureGroup(name=layer_name, show=False).add_to(m)
#         for l in range(hdf.shape[0]):
#             if hdf.loc[l, 'aerodrome'] == layer_name:
#                 if hdf.loc[l, 'obstacle_identifier'] == '792-55-A1-R1-40-0013':
#                     hdf.loc[l, 'coordinate'] = ('41.268954490 36.545948667 41.268945407 36.545976610 41.268935298 '
#                                                 '36.546001687 41.268911937 36.545996773 41.268906594 36.546008163 '
#                                                 '41.268860851 36.545985842 41.268873754 36.545940854 41.268895308 '
#                                                 '36.545889963 41.268915084 36.545843271 41.268954558 36.545870598 '
#                                                 '41.268935405 36.545917174 41.268929546 36.545931420 41.268954490 '
#                                                 '36.545948667')
#             if hdf.loc[l, 'geometry'].geom_type == 'MultiLineString':
#                 if len(hdf.loc[l, 'coordinate']) % 2 != 0:
#                     hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]
#
#                 if hdf.loc[l, 'coordinate'][-4::1] == ' 38*':
#                     hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-4]
#
#                 folium.PolyLine(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
#                                 color='green',
#                                 popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                                       f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     fg)
#
#
#
#             elif hdf.loc[l, 'geometry'].geom_type == 'MultiPolygon':
#                 if len(hdf.loc[l, 'coordinate']) % 2 != 0:
#                     hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]
#                 folium.Polygon(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
#                                color='green',
#                                popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                                      f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     fg)
#
#
#             elif hdf.loc[l, 'geometry'].geom_type == 'Point':
#                 coor = hdf.loc[l, 'coordinate'].replace(',', '.').split(' ')
#                 icons = folium.CustomIcon(
#                     icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/marker_dot.png')
#                 marker = folium.Marker(location=[coor[0], coor[1]], icon=icons, fill=True)
#                 popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                          f" Coordinates: {coor[0]}N, {coor[1]}E")
#
#                 folium.Popup(popup).add_to(marker)
#                 marker.add_to(fg)
#
#     folium.LayerControl().add_to(m)
#
#     frame = m.get_root()._repr_html_()
#     return render_template('mapping.html', frame=frame)


# if __name__ == '__main__':
#     app.run(debug=True, port=5002)


def chunks3(xs, n):
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
        coordinate_list[ind] = [t[0], t[1]]
    return coordinate_list

def marker_creator_ad(df, i, ):
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
engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db')
sql_ad = "SELECT * FROM ad_obstacles"
df_ad = pd.read_sql(sql_ad, con=engine)
print(df_ad.groupby('type').count())
# df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
# gdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
# dict_area2 = {}
# for p in path_list_area_2[:]:
#     dict_area2[str(p)[61:65].lower() + '_Area2a_Obstacles'] = folium.plugins.MarkerCluster(name=str(p)[61:65] + '_Area2a_Obstacles', control=True)
# print(dict_area2)



# def create_ad_obstacles_db(path_list):
#     """
# This function creates a database from .xml files for aerodrome obstacles for every airport in Turkey.
# All geometry is point.
#     :param path_list: Absolute path for every aerodrome obstacle xml file.
#     """
#
#     for i in path_list:
#
#         if path_list.index(i) == 0:
#             pass
#         else:
#             layer_name = str(i)[64:78]
#             bdf = geopandas.read_file(i)
#             bdf.to_file('aerodrome_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name, OVERWRITE='YES')
#
#
# # create_ad_obstacles_db(path_list_ad)
#
#
# def create_enr_obstacles_db():
#     """
#     This function creates a database from .xml file for AIP ENR 5.4 obstacles in Turkey.
#     All geometry is point.
#     """
#     df = geopandas.read_file(
#         '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml')
#     df.to_file('enr_obstacles.db', driver='SQLite')
#
#
# # create_enr_obstacles_db()
# def read_ad_enr_obs_db(db_path):
#     gdf = geopandas.read_file(db_path)
#     return gdf
#
#
# def create_area2a_db():
#     """
#     This function creates a database from .gdb files for area2a obstacles for every airport in Turkey. If data has crs type other
#     than WGS84 transforms it to WGS84. Also caution for file paths especially having space in it.
#     Geometry consists of point, and line
#
#     """
#     path_list = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
#     for i in path_list:
#         layer_name = str(i)[61:].replace('/', '_').replace('.gdb', '').lower()
#         bdf = geopandas.read_file(i, driver='OpenFileGDB')
#         if bdf.crs != 'EPSG:4326':
#             bdf = bdf.to_crs('EPSG:4326')
#         bdf.to_file('area2a_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)
#
#
# # create_area2a_db()
#
#
# def read_area2a():
#     path_list = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
#     for i in path_list:
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area2a_obstacles.db', echo=False)
#         layer_name = str(i)[61:].replace('/', '_').replace('.gdb', '').lower()
#         if path_list.index(i) == 0:
#             gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         else:
#             bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#             gdf = pd.concat([gdf, bdf], ignore_index=True)
#
#     return gdf
#
#
# def create_area_3_4_db(path_list, area: int, path_list_xml):
#     """
#     This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
#     LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
#     WGS84. Also caution for file paths especially having space in it.
#     Geometry consists of point, line, and polygon.
#     path_list: list of paths for .gdb files
#     area: area number, 3 or 4
#     path_list_xml: list of paths for .xml files which contains aerodrome data in it.
#     """
#     if area == 3:
#         for i in path_list:
#             layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
#             bdf = geopandas.read_file(i, driver='OpenFileGDB')
#             if bdf.crs != 'EPSG:4326':
#                 bdf = bdf.to_crs('EPSG:4326')
#             bdf.to_file('area3_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)
#
#     elif area == 4:
#         for i in path_list:
#             layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
#             bdf = geopandas.read_file(i, driver='OpenFileGDB')
#             if bdf.crs != 'EPSG:4326':
#                 bdf = bdf.to_crs('EPSG:4326')
#             bdf.to_file('area4_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)
#
#         for j in path_list_xml:
#             layer_name = str(j)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#             bdf = geopandas.read_file(j)
#             if bdf.crs != 'EPSG:4326':
#                 bdf = bdf.to_crs('EPSG:4326')
#             bdf.to_file('area4_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)
#     else:
#         print('Wrong area number. Please enter 3 or 4.')
#
#
# # create_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
# # create_area_3_4_db(path_list_area_4, 4, path_list_area_4_xml)
#
# def read_area_3_4_db(path_list, area: int, path_list_xml):
#     """
#     This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
#     LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
#     WGS84. Also caution for file paths especially having space in it. Sometimes manually changing file names may be better:).
#
#     """
#     if area == 3:
#         for i in path_list:
#             layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
#             engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area3_obstacles.db', echo=False)
#             if path_list.index(i) == 0:
#                 gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#             else:
#                 bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#                 gdf = pd.concat([gdf, bdf], ignore_index=True)
#
#     elif area == 4:
#         for j in path_list:
#             layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
#             engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#             if path_list.index(j) == 0:
#                 gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#             else:
#                 bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#                 gdf = pd.concat([gdf, bdf], ignore_index=True)
#
#         for k in path_list_xml:
#             layer_name = str(k)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#             engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#             if path_list_xml.index(k) == 0:
#                 xdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#             else:
#                 ydf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#                 xdf = pd.concat([xdf, ydf], ignore_index=True)
#         gdf = pd.concat([gdf, xdf], ignore_index=True)
#     else:
#         print('Wrong area number. Please enter 3 or 4.')
#     return gdf


# def area_2a_obstacles():
#     m4 = folium.Map(location=[39, 35], zoom_start=6)
#     engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
#     mc = MarkerCluster(name='Area2a_Obstacles', control=True)
#     sql_ad = f'''SELECT geo,coordinate,elevation, obstacle_type, aerodrome FROM area2a_obstacles'''
#     df_ad = pd.read_sql(sql_ad, con=engine)
#     df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
#     gdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
#     # dict_area2 = {}
#     # for p in path_list_area_2[:]:
#     #     dict_area2[str(p)[61:65].lower() + '_Area2a_Obstacles'] = MarkerCluster(name=str(p)[61:65] + '_Area2a_Obstacles', control=True)
#     for i in range(gdf.shape[0]):
#         coor = gdf.get_coordinates(ignore_index=True)
#         if gdf.loc[i, 'geometry'].geom_type == 'Point':
#             hh = gdf.loc[i, 'coordinate'].replace(',', '.').split(' ')
#             marker = folium.CircleMarker(location=(hh[0], hh[1]), radius=3, color='red',
#                                          fill=True, fill_opacity=1)
#             popup = (f"Elevation: {gdf.loc[i, 'elevation']} FT Type: {gdf.loc[i, 'obstacle_type']} "
#                      f" Coordinates: {coor.loc[i, 'y']}N, {coor.loc[i, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#
#             mc.add_child(marker)
#
#         elif gdf.loc[i, 'geometry'].geom_type == 'MultiLineString':
#             if gdf.loc[i, 'aerodrome'] == 'ltfe_Area2a_Obstacles':
#                 poly1 = folium.PolyLine(locations=chunks3(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
#                                         color='purple',
#                                         popup=f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} "
#                                               f" Coordinates(..N..E): {chunks3(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}")
#                 mc.add_child(poly1)
#             else:
#                 poly2 = folium.PolyLine(locations=chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
#                                         color='purple',
#                                         popup=f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} "
#                                               f" Coordinates(..N..E): {chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}")
#                 mc.add_child(poly2)
#         elif gdf.loc[i, 'geometry'].geom_type == 'MultiPolygon':
#             sky = folium.Polygon(locations=chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2),
#                                  color='purple',
#                                  popup=f"Elevation: {gdf.loc[i, 'elevation']} FT  Type: {gdf.loc[i, 'obstacle_type']} "
#                                        f" Coordinates(..N..E): {chunks2(gdf.loc[i, 'coordinate'].replace(',', '.').split(' '), 2)}")
#             mc.add_child(sky)
#         mc.add_to(m4)
#     folium.plugins.MousePosition().add_to(m4)
#     folium.LayerControl(collapsed=False).add_to(m4)
#     frame = m4.get_root().render()


# def read_all_area():
#     """
#     This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
#     LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
#     WGS84. Also caution for file paths especially having space in it.
#
#     """
#     maps = folium.Map(location=[39, 35], zoom_start=6)
#     engine = create_engine('sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'), echo=False)
#     fg = MarkerCluster(control=False)
#     maps.add_child(fg)
#     # g1 = folium.plugins.FeatureGroupSubGroup(fg, 'Ad_Obst')
#     # maps.add_child(g1)
#     g2 = FeatureGroupSubGroup(fg, 'Area 2a Obst')
#     maps.add_child(g2)
#     g3 = FeatureGroupSubGroup(fg, 'Area3_Obst')
#     maps.add_child(g3)
#     g5 = FeatureGroupSubGroup(fg, 'Area4_Obst')
#     maps.add_child(g5)
#
#     # for p in path_list_ad[:]:
#     #     ad = str(p)[64:68]
#     #     sql_ad = f'''SELECT geo,coordinate,elevation,type FROM ad_obstacles  where ad_obstacles.aerodrome="{str(p)[64:68].lower()}"'''
#     #     df_ad = pd.read_sql(sql_ad, con=engine)
#     #     df_ad['geometry'] = df_ad['geo'].apply(wkt.loads)
#     #     cdf = geopandas.GeoDataFrame(df_ad, crs='EPSG:4326')
#     #
#     #     for o in range(cdf.shape[0]):
#     #         coor = cdf.get_coordinates(ignore_index=True)
#     #         # icons = folium.CustomIcon(
#     #         #     icon_image='/Users/dersim/PycharmProjects/mapping/static/assets/images/marker_dot.png')
#     #         marker = folium.CircleMarker(location=[coor.loc[o, 'y'], coor.loc[o, 'x']], radius=3, color='purple', fill_opacity=1, fill=True)
#     #         popup = (f"Elevation: {cdf.loc[o, 'elevation']} FT Type: {cdf.loc[o, 'type']} "
#     #                  f" Coordinates: {coor.loc[o, 'y']}N, {coor.loc[o, 'x']}E")
#     #
#     #         folium.Popup(popup).add_to(marker)
#     #         marker.add_to(g1)
#
#     sql_a2 = f'''SELECT geo, coordinate, elevation, obstacle_type  FROM area2a_obstacles'''
#     df_a2 = pd.read_sql(sql_a2, con=engine)
#     df_a2['geometry'] = df_a2['geo'].apply(wkt.loads)
#     bdf = geopandas.GeoDataFrame(df_a2, crs='EPSG:4326')
#
#     for o in range(bdf.shape[0]):
#         coor = bdf.get_coordinates(ignore_index=True)
#
#         if bdf.loc[o, 'geometry'].geom_type == 'Point':
#             yy = bdf.loc[o, 'coordinate'].replace(',', '.').split(' ')
#             # icons = folium.CustomIcon(
#             #     icon_image='/app/static/assets/images/marker_dot.png')
#             marker = folium.CircleMarker(location=[yy[0], yy[1]], radius=3, color='blue',
#                                          fill_opacity=1, fill=True)
#             popup = (f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
#                      f" Coordinates: {coor.loc[o, 'y']}N, {coor.loc[o, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#             marker.add_to(g2)
#         elif bdf.loc[o, 'geometry'].geom_type == 'MultiLineString':
#             folium.PolyLine(locations=chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '), 2),
#                             color='red',
#                             popup=f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
#                                   f" Coordinates(..N..E): {chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g2)
#
#     sql_a3 = f'''SELECT geo, coordinate, elevation, obstacle_type   FROM area3_obstacles'''
#     df_a3 = pd.read_sql(sql_a3, con=engine)
#     df_a3['geometry'] = df_a3['geo'].apply(wkt.loads)
#     gdf = geopandas.GeoDataFrame(df_a3, crs='EPSG:4326')
#
#     coords = gdf.get_coordinates(ignore_index=True)
#     for t in range(gdf.shape[0]):
#
#         if gdf.loc[t, 'geometry'].geom_type == 'Point':
#             oo = gdf.loc[t, 'coordinate'].replace(',', '.').split(' ')
#             # icons = folium.CustomIcon(
#             #     icon_image='/app/static/assets/images/marker_dot.png')
#             marker = folium.CircleMarker(location=[oo[0], oo[1]], radius=3, color='magenta',
#                                          fill_opacity=1, fill=True)
#             popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
#                      f" Coordinates: {coords.loc[t, 'y']}N, {coords.loc[t, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#             marker.add_to(g3)
#
#         elif gdf.loc[t, 'geometry'].geom_type == 'MultiLineString':
#             folium.PolyLine(locations=chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
#                             color='purple',
#                             popup=f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
#                                   f" Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g3)
#
#     sql_ltac = "SELECT geo, Coordinate, Elevation, Obstacle_type  FROM ltac_area3_obstacles"
#     df_ltac = pd.read_sql(sql_ltac, con=engine)
#     df_ltac['geometry'] = df_ltac['geo'].apply(wkt.loads)
#     ltac = geopandas.GeoDataFrame(df_ltac, crs='EPSG:4326')
#
#     coord = ltac.get_coordinates(ignore_index=True)
#     for e in range(ltac.shape[0]):
#
#         if ltac.loc[e, 'geometry'].geom_type == 'Point':
#             uu = ltac.loc[e, 'Coordinate'].replace(',', '.').split(' ')
#             # icons = folium.CustomIcon(
#             #     icon_image='/app/static/assets/images/marker_dot.png')
#             marker = folium.CircleMarker(location=[uu[0], uu[1]], radius=3, color='pink',
#                                          fill_opacity=1, fill=True)
#             popup = (f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']}"
#                      f" Coordinates: {coord.loc[e, 'y']}N, {coord.loc[e, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#             marker.add_to(g3)
#
#         elif ltac.loc[e, 'geometry'].geom_type == 'LineString':
#             folium.PolyLine(locations=chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
#                             color='brown',
#                             popup=f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']} "
#                                   f" Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g3)
#
#
#         elif ltac.loc[e, 'geometry'].geom_type == 'Polygon':
#             folium.Polygon(locations=chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2),
#                            color='brown',
#                            popup=f"Elevation: {ltac.loc[e, 'Elevation']} FT  Type: {ltac.loc[e, 'Obstacle_Type']} "
#                                  f" Coordinates(..N..E): {chunks2(ltac.loc[e, 'Coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g3)
#
#     sql_a4 = f'''SELECT geo, coordinate, elevation, obstacle_type  FROM area4_obstacles'''
#     df_a4 = pd.read_sql(sql_a4, con=engine)
#     df_a4['geometry'] = df_a4['geo'].apply(wkt.loads)
#     hdf = geopandas.GeoDataFrame(df_a4, crs='EPSG:4326')
#
#     for l in range(hdf.shape[0]):
#         coordss = hdf.get_coordinates(ignore_index=True)
#         if len(hdf.loc[l, 'coordinate']) % 2 != 0:
#             hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]
#
#         if hdf.loc[l, 'coordinate'][-4::1] == ' 38*':
#             hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-4]
#
#         if hdf.loc[l, 'geometry'].geom_type == 'Point':
#             c = hdf.loc[l, 'coordinate'].replace(',', '.').split(' ')
#             # icons = folium.CustomIcon(
#             #     icon_image='/app/static/assets/images/marker_dot.png')
#             marker = folium.CircleMarker(location=[c[0], c[1]], radius=3, color='black',
#                                          fill_opacity=1, fill=True)
#             popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                      f" Coordinates: {coordss.loc[l, 'y']}N, {coordss.loc[l, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#             marker.add_to(g5)
#
#         elif hdf.loc[l, 'geometry'].geom_type == 'MultiLineString':
#             folium.PolyLine(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
#                             color='green',
#                             popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                                   f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g5)
#
#     sql_fm = "SELECT geo, coordinate, elevation,type  FROM ltfm_area4_obstacles"
#     df_fm = pd.read_sql(sql_fm, con=engine)
#     df_fm['geometry'] = df_fm['geo'].apply(wkt.loads)
#     xdf = geopandas.GeoDataFrame(df_fm, crs='EPSG:4326')
#
#     for u in range(xdf.shape[0]):
#         coorddss = xdf.get_coordinates(ignore_index=True)
#         if xdf.loc[u, 'geometry'].geom_type == 'Point':
#             gg = xdf.loc[u, 'coordinate'].replace(',', '.').split(' ')
#             # icons = folium.CustomIcon(
#             #     icon_image='/app/static/assets/images/marker_dot.png')
#             marker = folium.CircleMarker(location=[gg[1], gg[0]], radius=3,
#                                          color='yellow', fill_opacity=1, fill=True)
#             popup = (f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']}"
#                      f" Coordinates: {coorddss.loc[u, 'y']}N, {coorddss.loc[u, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#             marker.add_to(g5)
#
#         elif xdf.loc[u, 'geometry'].geom_type == 'MultiLineString':
#             folium.PolyLine(locations=chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
#                             color='brown',
#                             popup=f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']} "
#                                   f" Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g5)
#
#
#         elif xdf.loc[u, 'geometry'].geom_type == 'MultiPolygon':
#             folium.Polygon(locations=chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2),
#                            color='brown',
#                            popup=f"Elevation: {xdf.loc[u, 'elevation']} FT  Type: {xdf.loc[u, 'type']} "
#                                  f" Coordinates(..N..E): {chunks2(xdf.loc[u, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                 g5)
#
#     folium.LayerControl(collapsed=False).add_to(maps)
#     folium.plugins.MousePosition().add_to(maps)
#     frame = maps.get_root().render()
#     return frame
