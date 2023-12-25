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


def read_ltac_area3():
    engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=True)

    point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)

    for i in range(point_df.shape[0]):
        point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
                                                float(point_df.loc[i, 'Coordinate'].split(' ')[1]))

    line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
    for i in range(line_df.shape[0]):
        line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))

    pointline = pd.concat([point_df, line_df], ignore_index=True)

    polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)
    for i in range(polygon_df.shape[0]):

        if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
            polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
            polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
        else:
            polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))
    poly_point_line = pd.concat([polygon_df, pointline], ignore_index=True)
    return poly_point_line


ltac = read_ltac_area3()
ltac_gdf = geopandas.GeoDataFrame(ltac, geometry='GEOMETRY')

engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db', echo=False)
for j in path_list_area_4:
    layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
    hdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
    for l in range(hdf.shape[0]):
        if len(hdf.loc[l,'coordinate'])%2 != 0:
            hdf.loc[l, 'coordinate'] = hdf.loc[l, 'coordinate'][:-1]


#

print(type(str(path_list_area_2[:][0])))
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


# def create_obstacles_db(path_list_1, path_list_2, path_list_3, path_list_4, path_list_5, path_list_6):
#     for i in path_list_1:
#
#         if path_list_1.index(i) == 0:
#             pass
#         else:
#             layer_name_1 = str(i)[64:78]
#             adf = geopandas.read_file(i)
#             adf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_1)
#
#     bdf = geopandas.read_file(path_list_2)
#     bdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer='enr_obstacles')
#
#     for j in path_list_3:
#         layer_name_3 = str(j)[61:].replace('/', '_').replace('.gdb', '').lower()
#         cdf = geopandas.read_file(j, driver='OpenFileGDB')
#         if cdf.crs != 'EPSG:4326':
#             cdf = cdf.to_crs('EPSG:4326')
#         cdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_3)
#
#     ltac_gdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer='ltac_area_3_area_3')
#
#     for k in path_list_4:
#         layer_name_4 = str(k)[69:].replace('/', '_').replace('.gdb', '').lower()
#         ddf = geopandas.read_file(k, driver='OpenFileGDB')
#         if ddf.crs != 'EPSG:4326':
#             ddf = ddf.to_crs('EPSG:4326')
#         ddf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_4)
#
#     for l in path_list_5:
#         layer_name_5 = str(l)[69:].replace('/', '_').replace('.gdb', '').lower()
#         edf = geopandas.read_file(l, driver='OpenFileGDB')
#         if edf.crs != 'EPSG:4326':
#             edf = edf.to_crs('EPSG:4326')
#         edf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_5)
#
#     for m in path_list_6:
#         layer_name_6 = str(m)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#         fdf = geopandas.read_file(m)
#         if fdf.crs != 'EPSG:4326':
#             fdf = fdf.to_crs('EPSG:4326')
#         fdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_6)
#
#
# create_obstacles_db(path_list_ad, path_to_enr, path_list_area_2, path_list_area_3, path_list_area_4,
#                     path_list_area_4_xml)


# def read_alls(path_list_ad, path_list_enr, path_list_2, path_list_3, path_list_4, path_list_xml, maps):
#     engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/instance/obstacles.db', echo=False)
#     mcg = folium.plugins.MarkerCluster(control=False)
#     maps.add_child(mcg)
#
#     for i in path_list_1:
#
#             if path_list_1.index(i) == 0:
#                 pass
#             else:
#                 layer_name_1 = str(i)[64:78]
#                 adf = geopandas.read_file(i)
#                 adf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_1)
#
#         bdf = geopandas.read_file(path_list_2)
#         bdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer='enr_obstacles')
#
#         for j in path_list_3:
#             layer_name_3 = str(j)[61:].replace('/', '_').replace('.gdb', '').lower()
#             cdf = geopandas.read_file(j, driver='OpenFileGDB')
#             if cdf.crs != 'EPSG:4326':
#                 cdf = cdf.to_crs('EPSG:4326')
#             cdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_3)
#
#         ltac_gdf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer='ltac_area_3_area_3')
#
#         for k in path_list_4:
#             layer_name_4 = str(k)[69:].replace('/', '_').replace('.gdb', '').lower()
#             ddf = geopandas.read_file(k, driver='OpenFileGDB')
#             if ddf.crs != 'EPSG:4326':
#                 ddf = ddf.to_crs('EPSG:4326')
#             ddf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_4)
#
#         for l in path_list_5:
#             layer_name_5 = str(l)[69:].replace('/', '_').replace('.gdb', '').lower()
#             edf = geopandas.read_file(l, driver='OpenFileGDB')
#             if edf.crs != 'EPSG:4326':
#                 edf = edf.to_crs('EPSG:4326')
#             edf.to_file('obstacles.db', driver='SQLite', spatialite=True, layer=layer_name_5)
#
#         for m in path_list_6:
#             layer_name_6 = str(m)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#             fdf = geopandas.read_file(m)
#             if fdf.crs != 'EPSG:4326':
#                 fdf = fdf.to_crs('EPSG:4326')
#
#     ydf = read_ad_enr_obs_db(path_list_enr)
#     g0 = folium.plugins.FeatureGroupSubGroup(mcg, 'En-route Obstacles')
#     maps.add_child(g0)
#     for y in range(ydf.shape[0]):
#         coor = ydf.loc[y, 'geometry']
#         icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot_orange.png')
#         marker = folium.Marker(location=[coor.y, coor.x], icon=icons)
#         popup = (f"Elevation: {ydf.loc[y, 'elevation']} FT Type: {ydf.loc[y, 'type']} "
#                  f" Coordinates: {coor.y}N, {coor.x}E")
#
#         folium.Popup(popup).add_to(marker)
#         marker.add_to(g0)
#
#     for p in path_list_ad[1:]:
#         layer_name = str(p)[64:78].lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db', echo=False)
#         cdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#
#         g1 = folium.plugins.FeatureGroupSubGroup(mcg, str(p)[64:68] + '_AD_Obst')
#         maps.add_child(g1)
#         for o in range(cdf.shape[0]):
#             coor = cdf.get_coordinates(ignore_index=True)
#             icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
#             marker = folium.Marker(location=(coor.loc[o, 'y'], coor.loc[o, 'x']), icon=icons, color='yellow')
#             popup = (f"Elevation: {cdf.loc[o, 'elevation']} FT Type: {cdf.loc[o, 'type']} "
#                      f" Coordinates: {coor.loc[o, 'y']}N, {coor.loc[o, 'x']}E")
#
#             folium.Popup(popup).add_to(marker)
#             marker.add_to(g1)
#     for n in path_list_2:
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area2a_obstacles.db', echo=False)
#         layer_name = str(n)[61:].replace('/', '_').replace('.gdb', '').lower()
#         bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         g2 = folium.plugins.FeatureGroupSubGroup(mcg, f'{str(n)[61:65]}' + '_Area2a_Obst')
#         maps.add_child(g2)
#         for o in range(bdf.shape[0]):
#             coor = bdf.get_coordinates(ignore_index=True)
#             if bdf.loc[o, 'GEOMETRY'].geom_type == 'Point':
#                 icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
#                 marker = folium.Marker(location=(coor.loc[o, 'y'], coor.loc[o, 'x']), icon=icons, color='red')
#                 popup = (f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
#                          f" Coordinates: {coor.loc[o, 'y']}N, {coor.loc[o, 'x']}E")
#
#                 folium.Popup(popup).add_to(marker)
#                 marker.add_to(g2)
#             elif bdf.loc[o, 'GEOMETRY'].geom_type == 'MultiLineString':
#                 folium.PolyLine(locations=chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '), 2),
#                                 color='red',
#                                 popup=f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
#                                       f" Coordinates(..N..E): {chunks2(bdf.loc[o, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     g2)
#     g6 = folium.plugins.FeatureGroupSubGroup(mcg, 'LTAC_Area3_Obst')
#     maps.add_child(g6)
#     for e in range(line_df.shape[0]):
#         folium.PolyLine(locations=chunks2(line_df.loc[e, 'Coordinate'].split(' '), 2), color='red',
#                         popup=f"Elevation: {line_df.loc[e, 'Elevation']} FT  Type: {line_df.loc[e, 'Obstacle_Type']} "
#                               f" Coordinates(..N..E): {chunks2(line_df.loc[e, 'Coordinate'].split(' '), 2)}").add_to(g6)
#
#     for w in range(polygon_df.shape[0]):
#         folium.Polygon(locations=chunks2(polygon_df.loc[w, 'Coordinate'].split(' '), 2), color='red',
#                        popup=f"Elevation: {polygon_df.loc[w, 'Elevation']} FT  Type: {polygon_df.loc[w, 'Obstacle_Type']} "
#                              f" Coordinates(..N..E): {chunks2(polygon_df.loc[w, 'Coordinate'].split(' '), 2)}").add_to(
#             g6)
#
#     for c in range(point_gdf.shape[0]):
#         coords = point_gdf.loc[c, 'GEOMETRY']
#         icon_images = '/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png'
#         folium.Marker(location=[coords.x, coords.y],
#                       icon=folium.CustomIcon(icon_image=icon_images, icon_size=(8, 8)), color='red',
#                       popup=f"Elevation: {point_gdf.loc[c, 'Elevation']} Type: {point_gdf.loc[c, 'Obstacle_Type']} "
#                             f" Coordinates: {coords.y}N, {coords.x}E").add_to(g6)
#     for i in path_list_3:
#         layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area3_obstacles.db', echo=False)
#         gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         g3 = folium.plugins.FeatureGroupSubGroup(mcg, str(i)[69:73] + '_Area3_Obst')
#         maps.add_child(g3)
#         for t in range(gdf.shape[0]):
#             coor = gdf.get_coordinates(ignore_index=True)
#             if gdf.loc[t, 'GEOMETRY'].geom_type == 'Point':
#                 icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
#                 marker = folium.Marker(location=(coor.loc[t, 'y'], coor.loc[t, 'x']), icon=icons, color='purple')
#                 popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
#                          f" Coordinates: {coor.loc[t, 'y']}N, {coor.loc[t, 'x']}E")
#
#                 folium.Popup(popup).add_to(marker)
#                 marker.add_to(g3)
#
#             elif gdf.loc[t, 'GEOMETRY'].geom_type == 'MultiLineString':
#                 folium.PolyLine(locations=chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2),
#                                 color='purple',
#                                 popup=f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
#                                       f" Coordinates(..N..E): {chunks2(gdf.loc[t, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     g3)
#
#     for j in path_list_4:
#         layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#         hdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         g4 = folium.plugins.FeatureGroupSubGroup(mcg, str(j)[69:73] + '_Area4_Obst')
#         maps.add_child(g4)
#
#         for l in range(hdf.shape[0]):
#             coor = hdf.get_coordinates(ignore_index=True)
#             if hdf.loc[l, 'GEOMETRY'].geom_type == 'Point':
#                 icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
#                 marker = folium.Marker(location=(coor.loc[l, 'y'], coor.loc[l, 'x']), icon=icons, color='green')
#                 popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                          f" Coordinates: {coor.loc[l, 'y']}N, {coor.loc[l, 'x']}E")
#
#                 folium.Popup(popup).add_to(marker)
#                 marker.add_to(g4)
#
#             elif hdf.loc[l, 'GEOMETRY'].geom_type == 'MultiLineString':
#                 folium.PolyLine(locations=chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2),
#                                 color='green',
#                                 popup=f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
#                                       f" Coordinates(..N..E): {chunks2(hdf.loc[l, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     g4)
#     for k in path_list_xml:
#         layer_name = str(k)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
#         engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
#         xdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
#         g5 = folium.plugins.FeatureGroupSubGroup(mcg, str(k)[69:73] + 'Area4_Obstacles')
#         maps.add_child(g5)
#         for m in range(xdf.shape[0]):
#             coor = xdf.get_coordinates(ignore_index=True)
#             if xdf.loc[m, 'GEOMETRY'].geom_type == 'Point':
#                 icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
#                 marker = folium.Marker(location=(coor.loc[m, 'y'], coor.loc[m, 'x']), icon=icons, color='brown')
#                 popup = (f"Elevation: {xdf.loc[m, 'elevation']} FT  Type: {xdf.loc[m, 'type']}"
#                          f" Coordinates: {coor.loc[m, 'y']}N, {coor.loc[m, 'x']}E")
#
#                 folium.Popup(popup).add_to(marker)
#                 marker.add_to(g5)
#
#             elif xdf.loc[m, 'GEOMETRY'].geom_type == 'MultiLineString':
#                 folium.PolyLine(locations=chunks2(xdf.loc[m, 'coordinate'].replace(',', '.').split(' '), 2),
#                                 color='brown',
#                                 popup=f"Elevation: {xdf.loc[m, 'elevation']} FT  Type: {xdf.loc[m, 'type']} "
#                                       f" Coordinates(..N..E): {chunks2(xdf.loc[m, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     g5)
#
#
#             elif xdf.loc[m, 'GEOMETRY'].geom_type == 'MultiPolygon':
#                 folium.Polygon(locations=chunks2(xdf.loc[m, 'coordinate'].replace(',', '.').split(' '), 2),
#                                color='brown',
#                                popup=f"Elevation: {xdf.loc[m, 'elevation']} FT  Type: {xdf.loc[m, 'type']} "
#                                      f" Coordinates(..N..E): {chunks2(xdf.loc[m, 'coordinate'].replace(',', '.').split(' '), 2)}").add_to(
#                     g5)