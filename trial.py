import folium
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
from geoalchemy2 import Geometry

secret_key = os.environ.get('SECRET_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obstacles.db'
db = SQLAlchemy()
db.init_app(app)

path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_to_enr = '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml'
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))

secret_key = os.environ.get('SECRET_KEY')
print(secret_key)
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

engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db', echo=False)
for j in path_list_area_4:
    layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
    hdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
    for l in range(hdf.shape[0]):
        if len(hdf.loc[l,'coordinate'])%2 != 0:
            hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]


#

print(str(path_list_area_2[:][0])[61:].replace('/', '_').replace('.gdb', '').lower())
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

# engine = create_engine('postgresql://postgres:8488@localhost/obstacles', echo=True)
# metadata = MetaData()
# ad_obstacles = Table('ad_obstacles', metadata,
#                      Column('id', Integer, primary_key=True),
#                      Column('coordinate', String),
#                      Column('GEOMETRY', Geometry('GEOMETRY')),
#                      Column('gml_id', String),
#                      Column('identifier', String),
#                      Column('beginposition', String),
#                      Column('interpretation', String),
#                      Column('sequencenumber', Integer),
#                      Column('correctionnumber', Integer),
#                      Column('timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition', String),
#                      Column('name', String),
#                      Column('type', String),
#                      Column('lighted', String),
#                      Column('group', String),
#                      Column('verticalextent', Float),
#                      Column('verticalextent_uom', String),
#                      Column('timeslice_verticalstructuretimeslice_part_verticalstructurepart_type', String),
#                      Column('designator', String),
#                      Column('elevation', Float),
#                      Column('elevation_uom', String),
#                      Column('colour', String))
#
# ad_obstacles.create(engine)
# metadata.create_all(engine)

# class AerodromeObstacles(db.Model):
#     __tablename__ = "ad_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     coordinate = db.Column(db.String())
#     gml_id = db.Column(db.String())
#     identifier = db.Column(db.String())
#     beginposition = db.Column(db.String())
#     interpretation = db.Column(db.String())
#     sequencenumber = db.Column(db.Integer)
#     correctionnumber = db.Column(db.Integer)
#     timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
#     name = db.Column(db.String())
#     type = db.Column(db.String())
#     lighted = db.Column(db.String())
#     group = db.Column(db.String())
#     verticalextent = db.Column(db.Float)
#     verticalextent_uom = db.Column(db.String())
#     timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
#     designator = db.Column(db.String())
#     elevation = db.Column(db.Float)
#     elevation_uom = db.Column(db.String())
#     colour = db.Column(db.String())


# class EnrouteObstacles(db.Model):
#     __tablename__ = "enr_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     coordinate = db.Column(db.String())
#     gml_id = db.Column(db.String())
#     identifier = db.Column(db.String())
#     beginposition = db.Column(db.String())
#     interpretation = db.Column(db.String())
#     sequencenumber = db.Column(db.Integer)
#     correctionnumber = db.Column(db.Integer)
#     timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
#     name = db.Column(db.String())
#     type = db.Column(db.String())
#     lighted = db.Column(db.String())
#     group = db.Column(db.String())
#     verticalextent = db.Column(db.Integer)
#     verticalextent_uom = db.Column(db.String())
#     timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
#     designator = db.Column(db.String())
#     elevation = db.Column(db.Integer)
#     elevation_uom = db.Column(db.String())
#     colour = db.Column(db.String())
#
#
# class Area2aObstacles(db.Model):
#     __tablename__ = "area2a_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     obstacle_identifier = db.Column(db.String())
#     horizontal_accuracy = db.Column(db.Float)
#     horizontal_confidence_level = db.Column(db.Integer)
#     elevation = db.Column(db.Float)
#     height = db.Column(db.Float)
#     vertical_accuracy = db.Column(db.Float)
#     vertical_confidence_level = db.Column(db.Integer)
#     obstacle_type = db.Column(db.String())
#     integrity = db.Column(db.String())
#     date_and_time_stamp = db.Column(db.String())
#     operations = db.Column(db.String())
#     effectivity = db.Column(db.String())
#     lighting = db.Column(db.String())
#     marking = db.Column(db.String())
#     horizontal_extent = db.Column(db.String())
#     obstacle_name = db.Column(db.String())
#     marking_details = db.Column(db.String())
#     lighting_color = db.Column(db.String())
#     coordinate = db.Column(db.String())
#     shape_length = db.Column(db.Float)
#     area = db.Column(db.String())
#
#
# class Area3Obstacles(db.Model):
#     __tablename__ = "area3_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     obstacle_identifier = db.Column(db.String())
#     horizontal_accuracy = db.Column(db.Float)
#     horizontal_confidence_level = db.Column(db.Integer)
#     elevation = db.Column(db.Float)
#     height = db.Column(db.Float)
#     vertical_accuracy = db.Column(db.Float)
#     vertical_confidence_level = db.Column(db.Integer)
#     obstacle_type = db.Column(db.String())
#     integrity = db.Column(db.String())
#     date_and_time_stamp = db.Column(db.String())
#     operations = db.Column(db.String())
#     effectivity = db.Column(db.String())
#     lighting = db.Column(db.String())
#     marking = db.Column(db.String())
#     obstacle_name = db.Column(db.String())
#     lighting_color = db.Column(db.String())
#     marking_details = db.Column(db.String())
#     coordinate = db.Column(db.String())
#     horizontal_extent = db.Column(db.String())
#     shape_length = db.Column(db.Float)
#
#
# class LtacArea3Obstacles(db.Model):
#     __tablename__ = "ltac_area3_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     Obstacle_Identifier = db.Column(db.String())
#     Horizontal_Accuracy = db.Column(db.Float)
#     Horizontal_Confidence_Level = db.Column(db.Integer)
#     Elevation = db.Column(db.Float)
#     Height = db.Column(db.Float)
#     Vertical_Accuracy = db.Column(db.Float)
#     Vertical_Confidence_Level = db.Column(db.Integer)
#     Obstacle_Type = db.Column(db.String())
#     Integrity = db.Column(db.String())
#     Date_And_Time_Stamp = db.Column(db.String())
#     Operations = db.Column(db.String())
#     Effectivity = db.Column(db.String())
#     Lighting = db.Column(db.String())
#     Marking = db.Column(db.String())
#     Obstacle_Name = db.Column(db.String())
#     Lighting_Color = db.Column(db.String())
#     Marking_Details = db.Column(db.String())
#     Coordinate = db.Column(db.String())
#     SHAPE_Length = db.Column(db.Float)
#     SHAPE_Area = db.Column(db.String())
#     horizontal_extent = db.Column(db.String())
#
#
# class Area4Obstacles(db.Model):
#     __tablename__ = "area4_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     obstacle_identifier = db.Column(db.String())
#     horizontal_accuracy = db.Column(db.Float)
#     horizontal_confidence_level = db.Column(db.Integer)
#     elevation = db.Column(db.Float)
#     height = db.Column(db.Float)
#     vertical_accuracy = db.Column(db.Float)
#     vertical_confidence_level = db.Column(db.Integer)
#     obstacle_type = db.Column(db.String())
#     integrity = db.Column(db.String())
#     date_and_time_stamp = db.Column(db.String())
#     operations = db.Column(db.String())
#     effectivity = db.Column(db.String())
#     lighting = db.Column(db.String())
#     marking = db.Column(db.String())
#     horizontal_extent = db.Column(db.String())
#     obstacle_name = db.Column(db.String())
#     marking_details = db.Column(db.String())
#     lighting_color = db.Column(db.String())
#     coordinate = db.Column(db.String())
#     shape_length = db.Column(db.Float)
#     shape_area = db.Column(db.String())
#
#
# class LtfmArea4Obstacles(db.Model):
#     __tablename__ = "ltfm_area4_obstacles"
#     id = db.Column(db.Integer, primary_key=True)
#     coordinate = db.Column(db.String())
#     gml_id = db.Column(db.String())
#     identifier = db.Column(db.String())
#     beginposition = db.Column(db.String())
#     interpretation = db.Column(db.String())
#     sequencenumber = db.Column(db.Float)
#     correctionnumber = db.Column(db.Float)
#     timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition = db.Column(db.String())
#     name = db.Column(db.String())
#     type = db.Column(db.String())
#     lighted = db.Column(db.String())
#     group = db.Column(db.String())
#     verticalextent = db.Column(db.Float)
#     verticalextent_uom = db.Column(db.String())
#     timeslice_verticalstructuretimeslice_part_verticalstructurepart_type = db.Column(db.String())
#     designator = db.Column(db.Float)
#     elevation = db.Column(db.Float)
#     elevation_uom = db.Column(db.String())
#     colour = db.Column(db.String())


# ad_df = read_ad_obs(path_list_ad)


# area_2a = read_area2a()
# area_3_df = read_area_3_4_db(path_list_area_3, 3)
# area_4_df = read_area_3_4_db(path_list_area_4, 4)
# ltfm_area4_df = read_ltfm_area_4_xml(path_list_area_4_xml)
# ltac_area3 = read_ltac_area3()
# enr_df = read_enr_obs_db(path_to_enr)
# print(ad_df.geom_type)

# with app.app_context():
#     result = db.session.execute(db.select(Area3Obstacles)).scalars().all()

# print(ad_df.dtypes)
# print(area_2a_df.dtypes)
# print(area_3_df.dtypes)
# print(ltfm_area4_df.dtypes)
# print(area_4_df.dtypes)


# print(enr_df.dtypes)
# print(ltac_area3.dtypes)


# coord_list = []
#
# coords = ad_df.get_coordinates()
# for i in range(ad_df.shape[0]):
#     coord_list.append([float(coords.loc[i].x), float(coords.loc[i].y)])
#
#     ad_obstacle = AerodromeObstacles(coordinate=f"{coord_list[i][0]} {coord_list[i][1]}",
#                                      gml_id=ad_df.loc[i, 'gml_id'],
#                                      identifier=ad_df.loc[i, 'identifier'],
#                                      beginposition=ad_df.loc[i, 'beginposition'],
#                                      interpretation=ad_df.loc[i, 'interpretation'],
#                                      sequencenumber=ad_df.loc[i, 'sequencenumber'],
#                                      correctionnumber=ad_df.loc[i, 'correctionnumber'],
#                                      timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                      ad_df.loc[
#                                          i, 'timeslice|verticalstructuretimeslice|featurelifetime|timeperiod|beginposition'],
#                                      name=ad_df.loc[i, 'name'],
#                                      type=ad_df.loc[i, 'type'],
#                                      lighted=ad_df.loc[i, 'lighted'],
#                                      group=ad_df.loc[i, 'group'],
#                                      verticalextent=ad_df.loc[i, 'verticalextent'],
#                                      verticalextent_uom=ad_df.loc[i, 'verticalextent_uom'],
#                                      timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ad_df.loc[
#                                          i, 'timeslice|verticalstructuretimeslice|part|verticalstructurepart|type'],
#                                      designator=ad_df.loc[i, 'designator'],
#                                      elevation=ad_df.loc[i, 'elevation'],
#                                      elevation_uom=ad_df.loc[i, 'elevation_uom'],
#                                      colour=ad_df.loc[i, 'colour'])
#     db.session.add(ad_obstacle)
#     db.session.commit()
#
# enr_coords = enr_df.get_coordinates()
# coord_list_enr = []
# for i in range(enr_df.shape[0]):
#     coord_list_enr.append([float(enr_coords.loc[i].x), float(enr_coords.loc[i].y)])
#     enr_obstacles = EnrouteObstacles(coordinate=f"{coord_list_enr[i][0]} {coord_list_enr[i][1]}",
#                                      gml_id=enr_df.loc[i, 'gml_id'],
#                                      identifier=enr_df.loc[i, 'identifier'],
#                                      beginposition=enr_df.loc[i, 'beginPosition'],
#                                      interpretation=enr_df.loc[i, 'interpretation'],
#                                      sequencenumber=enr_df.loc[i, 'sequenceNumber'],
#                                      correctionnumber=enr_df.loc[i, 'correctionNumber'],
#                                      timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                      enr_df.loc[
#                                          i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
#                                      name=enr_df.loc[i, 'name'],
#                                      type=enr_df.loc[i, 'type'],
#                                      lighted=enr_df.loc[i, 'lighted'],
#                                      group=enr_df.loc[i, 'group'],
#                                      verticalextent=enr_df.loc[i, 'verticalExtent'],
#                                      verticalextent_uom=enr_df.loc[i, 'verticalExtent_uom'],
#                                      timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=enr_df.loc[
#                                          i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
#                                      designator=enr_df.loc[i, 'designator'],
#                                      elevation=enr_df.loc[i, 'elevation'],
#                                      elevation_uom=enr_df.loc[i, 'elevation_uom'],
#                                      colour=enr_df.loc[i, 'colour'])
#     db.session.add(enr_obstacles)
#     db.session.commit()
#
# for i in range(area_2a.shape[0]):
#     area2a_obstacles = Area2aObstacles(obstacle_identifier=area_2a.loc[i, 'obstacle_identifier'],
#                                        horizontal_accuracy=area_2a.loc[i, 'horizontal_accuracy'],
#                                        horizontal_confidence_level=area_2a.loc[i, 'horizontal_confidence_level'],
#                                        elevation=area_2a.loc[i, 'elevation'],
#                                        height=area_2a.loc[i, 'height'],
#                                        vertical_accuracy=area_2a.loc[i, 'vertical_accuracy'],
#                                        vertical_confidence_level=area_2a.loc[i, 'vertical_confidence_level'],
#                                        obstacle_type=area_2a.loc[i, 'obstacle_type'],
#                                        integrity=area_2a.loc[i, 'integrity'],
#                                        date_and_time_stamp=area_2a.loc[i, 'date_and_time_stamp'],
#                                        operations=area_2a.loc[i, 'operations'],
#                                        effectivity=area_2a.loc[i, 'effectivity'],
#                                        lighting=area_2a.loc[i, 'lighting'],
#                                        marking=area_2a.loc[i, 'marking'],
#                                        horizontal_extent=area_2a.loc[i, 'horizontal_extent'],
#                                        obstacle_name=area_2a.loc[i, 'obstacle_name'],
#                                        marking_details=area_2a.loc[i, 'marking_details'],
#                                        lighting_color=area_2a.loc[i, 'lighting_color'],
#                                        coordinate=area_2a.loc[i, 'coordinate'],
#                                        shape_length=area_2a.loc[i, 'shape_length'],
#                                        area=area_2a.loc[i, 'area'])
#
#     db.session.add(area2a_obstacles)
#     db.session.commit()
#
# for i in range(area_3_df.shape[0]):
#     area3_obstacles = Area3Obstacles(obstacle_identifier=area_3_df.loc[i, 'obstacle_identifier'],
#                                      horizontal_accuracy=area_3_df.loc[i, 'horizontal_accuracy'],
#                                      horizontal_confidence_level=area_3_df.loc[
#                                          i, 'horizontal_confidence_level'],
#                                      elevation=area_3_df.loc[i, 'elevation'],
#                                      height=area_3_df.loc[i, 'height'],
#                                      vertical_accuracy=area_3_df.loc[i, 'vertical_accuracy'],
#                                      vertical_confidence_level=area_3_df.loc[i, 'vertical_confidence_level'],
#                                      obstacle_type=area_3_df.loc[i, 'obstacle_type'],
#                                      integrity=area_3_df.loc[i, 'integrity'],
#                                      date_and_time_stamp=area_3_df.loc[i, 'date_and_time_stamp'],
#                                      operations=area_3_df.loc[i, 'operations'],
#                                      effectivity=area_3_df.loc[i, 'effectivity'],
#                                      lighting=area_3_df.loc[i, 'lighting'],
#                                      marking=area_3_df.loc[i, 'marking'],
#                                      obstacle_name=area_3_df.loc[i, 'obstacle_name'],
#                                      lighting_color=area_3_df.loc[i, 'lighting_color'],
#                                      marking_details=area_3_df.loc[i, 'marking_details'],
#                                      coordinate=area_3_df.loc[i, 'coordinate'],
#                                      horizontal_extent=area_3_df.loc[i, 'horizontal_extent'],
#                                      shape_length=area_3_df.loc[i, 'shape_length'],
#                                      )
#
#     db.session.add(area3_obstacles)
#     db.session.commit()
#
# for i in range(ltac_area3.shape[0]):
#     ltac_area3_obstacles = LtacArea3Obstacles(Obstacle_Identifier=ltac_area3.loc[i, 'Obstacle_Identifier'],
#                                               Horizontal_Accuracy=ltac_area3.loc[i, 'Horizontal_Accuracy'],
#                                               Horizontal_Confidence_Level=ltac_area3.loc[
#                                                   i, 'Horizontal_Confidence_Level'],
#                                               Elevation=ltac_area3.loc[i, 'Elevation'],
#                                               Height=ltac_area3.loc[i, 'Height'],
#                                               Vertical_Accuracy=ltac_area3.loc[i, 'Vertical_Accuracy'],
#                                               Vertical_Confidence_Level=ltac_area3.loc[
#                                                   i, 'Vertical_Confidence_Level'],
#                                               Obstacle_Type=ltac_area3.loc[i, 'Obstacle_Type'],
#                                               Integrity=ltac_area3.loc[i, 'Integrity'],
#                                               Date_And_Time_Stamp=ltac_area3.loc[i, 'Date_And_Time_Stamp'],
#                                               Operations=ltac_area3.loc[i, 'Operations'],
#                                               Effectivity=ltac_area3.loc[i, 'Effectivity'],
#                                               Lighting=ltac_area3.loc[i, 'Lighting'],
#                                               Marking=ltac_area3.loc[i, 'Marking'],
#                                               Obstacle_Name=ltac_area3.loc[i, 'Obstacle_Name'],
#                                               Lighting_Color=ltac_area3.loc[i, 'Lighting_Color'],
#                                               Marking_Details=ltac_area3.loc[i, 'Marking_Details'],
#                                               Coordinate=ltac_area3.loc[i, 'Coordinate'],
#                                               SHAPE_Length=ltac_area3.loc[i, 'SHAPE_Length'],
#                                               SHAPE_Area=ltac_area3.loc[i, 'SHAPE_Area'],
#                                               horizontal_extent=ltac_area3.loc[i, 'Horizontal_Extent'])
#
#     db.session.add(ltac_area3_obstacles)
#     db.session.commit()
#
# for i in range(area_4_df.shape[0]):
#     area4_obstacles = Area4Obstacles(obstacle_identifier=area_4_df.loc[i, 'obstacle_identifier'],
#                                      horizontal_accuracy=area_4_df.loc[i, 'horizontal_accuracy'],
#                                      horizontal_confidence_level=area_4_df.loc[
#                                          i, 'horizontal_confidence_level'],
#                                      elevation=area_4_df.loc[i, 'elevation'],
#                                      height=area_4_df.loc[i, 'height'],
#                                      vertical_accuracy=area_4_df.loc[i, 'vertical_accuracy'],
#                                      vertical_confidence_level=area_4_df.loc[i, 'vertical_confidence_level'],
#                                      obstacle_type=area_4_df.loc[i, 'obstacle_type'],
#                                      integrity=area_4_df.loc[i, 'integrity'],
#                                      date_and_time_stamp=area_4_df.loc[i, 'date_and_time_stamp'],
#                                      operations=area_4_df.loc[i, 'operations'],
#                                      effectivity=area_4_df.loc[i, 'effectivity'],
#                                      lighting=area_4_df.loc[i, 'lighting'],
#                                      marking=area_4_df.loc[i, 'marking'],
#                                      horizontal_extent=area_4_df.loc[i, 'horizontal_extent'],
#                                      obstacle_name=area_4_df.loc[i, 'obstacle_name'],
#                                      marking_details=area_4_df.loc[i, 'marking_details'],
#                                      lighting_color=area_4_df.loc[i, 'lighting_color'],
#                                      coordinate=area_4_df.loc[i, 'coordinate'],
#                                      shape_length=area_4_df.loc[i, 'shape_length'],
#                                      shape_area=area_4_df.loc[i, 'shape_area'])
#
#     db.session.add(area4_obstacles)
#     db.session.commit()
#
# coord_list_ltfm = []
# coords = ltfm_area4_df.get_coordinates()
# for i in range(ltfm_area4_df.shape[0]):
#     coord_list_ltfm.append([float(coords.loc[i].x), float(coords.loc[i].y)])
#     ltfm_area4_obstacles = LtfmArea4Obstacles(coordinate=f"{coord_list_ltfm[i][0]} {coord_list_ltfm[i][1]}",
#                                               gml_id=ltfm_area4_df.loc[i, 'gml_id'],
#                                               identifier=ltfm_area4_df.loc[i, 'identifier'],
#                                               beginposition=ltfm_area4_df.loc[i, 'beginposition'],
#                                               interpretation=ltfm_area4_df.loc[i, 'interpretation'],
#                                               sequencenumber=ltfm_area4_df.loc[i, 'sequencenumber'],
#                                               correctionnumber=ltfm_area4_df.loc[i, 'correctionnumber'],
#                                               timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
#                                               ltfm_area4_df.loc[
#                                                   i, 'timeslice|verticalstructuretimeslice|featurelifetime|timeperiod|beginposition'],
#                                               name=ltfm_area4_df.loc[i, 'name'],
#                                               type=ltfm_area4_df.loc[i, 'type'],
#                                               lighted=ltfm_area4_df.loc[i, 'lighted'],
#                                               group=ltfm_area4_df.loc[i, 'group'],
#                                               verticalextent=ltfm_area4_df.loc[i, 'verticalextent'],
#                                               verticalextent_uom=ltfm_area4_df.loc[i, 'verticalextent_uom'],
#                                               timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=
#                                               ltfm_area4_df.loc[
#                                                   i, 'timeslice|verticalstructuretimeslice|part|verticalstructurepart'
#                                                      '|type'],
#                                               designator=ltfm_area4_df.loc[i, 'designator'],
#                                               elevation=ltfm_area4_df.loc[i, 'elevation'],
#                                               elevation_uom=ltfm_area4_df.loc[i, 'elevation_uom'],
#                                               colour=ltfm_area4_df.loc[i, 'colour'])
#     db.session.add(ltfm_area4_obstacles)
#     db.session.commit()

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)



# """
# Area 3 LTAC Obstacles are in format of .mdb. To handle that https://fishcodelib.com/index.htm has a tool called
# db.Migration.Net which converts .mdb to .sqlite. Then we can use geopandas to read the .sqlite file."""
# """ Getting data from ltac_obstacles.db which is created from .mdb file. """
# engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=True)
#
# point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)
#
# for i in range(point_df.shape[0]):
#     point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
#                                             float(point_df.loc[i, 'Coordinate'].split(' ')[1]))
#
# point_gdf = geopandas.GeoDataFrame(point_df, geometry='GEOMETRY', crs='EPSG:4326')
#
# line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
# for i in range(line_df.shape[0]):
#     line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))
#
# line_gdf = geopandas.GeoDataFrame(line_df, geometry='GEOMETRY', crs='EPSG:4326')
#
# polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)
# for i in range(polygon_df.shape[0]):
#
#     if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
#         polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
#         polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
#     else:
#         polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))
#
# polygon_gdf = geopandas.GeoDataFrame(polygon_df, geometry='GEOMETRY', crs='EPSG:4326')
# """ Getting data from ltac_obstacles.db which is created from .mdb file. """

