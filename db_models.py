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
pathfile = os.environ.get('pathfile')
secret_key = os.environ.get('SECRET_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'dev_key',
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://') or \
                            'sqlite:///' + os.path.join(app.instance_path, 'obstacles.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db = SQLAlchemy()
db.init_app(app)


path_list_ad = sorted(Path(pathfile +'/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_to_enr = sorted(Path(pathfile +'/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles').rglob("*.xml"))
path_list_area_2 = sorted(Path(pathfile +'/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path(pathfile +'/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path(pathfile +'/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path(pathfile +'/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))

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



for p in path_list_ad[:]:
    ad_df = geopandas.read_file(p)
    table = str(p)[64:68].lower()
    coord_list = []
    coords = ad_df.get_coordinates()
    for i in range(ad_df.shape[0]):
        ad_df['aerodrome'] = table
        coord_list.append([float(coords.loc[i].x), float(coords.loc[i].y)])
        try:
            with app.app_context():

                new = AerodromeObstacles(aerodrome=ad_df.loc[i, 'aerodrome'],
                                         coordinate=f"{coord_list[i][0]} {coord_list[i][1]}",
                                         gml_id=ad_df.loc[i, 'gml_id'],
                                         identifier=ad_df.loc[i, 'identifier'],
                                         beginposition=ad_df.loc[i, 'beginPosition'],
                                         interpretation=ad_df.loc[i, 'interpretation'],
                                         sequencenumber=ad_df.loc[i, 'sequenceNumber'],
                                         correctionnumber=ad_df.loc[i, 'correctionNumber'],
                                         timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
                                         ad_df.loc[
                                             i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
                                         name=ad_df.loc[i, 'name'], type=ad_df.loc[i, 'type'],
                                         lighted=ad_df.loc[i, 'lighted'],
                                         group=ad_df.loc[i, 'group'], verticalextent=ad_df.loc[i, 'verticalExtent'],
                                         verticalextent_uom=ad_df.loc[i, 'verticalExtent_uom'],
                                         timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ad_df.loc[
                                             i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
                                         designator=ad_df.loc[i, 'designator'], elevation=ad_df.loc[i, 'elevation'],
                                         elevation_uom=ad_df.loc[i, 'elevation_uom'], colour=ad_df.loc[i, 'colour'],
                                         geo= str(ad_df.loc[i, 'geometry']))

                db.session.add(new)
                db.session.commit()

        except KeyError:
            ad_df.loc[i, 'colour'] = 'NULL'
            with app.app_context():
                new = AerodromeObstacles(aerodrome=ad_df.loc[i, 'aerodrome'],
                                         coordinate=f"{coord_list[i][0]} {coord_list[i][1]}",
                                         gml_id=ad_df.loc[i, 'gml_id'],
                                         identifier=ad_df.loc[i, 'identifier'],
                                         beginposition=ad_df.loc[i, 'beginPosition'],
                                         interpretation=ad_df.loc[i, 'interpretation'],
                                         sequencenumber=ad_df.loc[i, 'sequenceNumber'],
                                         correctionnumber=ad_df.loc[i, 'correctionNumber'],
                                         timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
                                         ad_df.loc[
                                             i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
                                         name=ad_df.loc[i, 'name'], type=ad_df.loc[i, 'type'],
                                         lighted=ad_df.loc[i, 'lighted'],
                                         group=ad_df.loc[i, 'group'], verticalextent=ad_df.loc[i, 'verticalExtent'],
                                         verticalextent_uom=ad_df.loc[i, 'verticalExtent_uom'],
                                         timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ad_df.loc[
                                             i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
                                         designator=ad_df.loc[i, 'designator'], elevation=ad_df.loc[i, 'elevation'],
                                         elevation_uom=ad_df.loc[i, 'elevation_uom'], colour=ad_df.loc[i, 'colour'],
                                         geo= str(ad_df.loc[i, 'geometry']))
                db.session.add(new)
                db.session.commit()


for r in path_to_enr[1:]:
    table = str(r)[65:68] + str(r)[73:82]
    enr_df = geopandas.read_file(r)
    enr_coords = enr_df.get_coordinates()
    coord_list_enr = []
    for i in range(enr_df.shape[0]):
        coord_list_enr.append([float(enr_coords.loc[i].x), float(enr_coords.loc[i].y)])
        with app.app_context():
            enr_obstacles = EnrouteObstacles(coordinate=f"{coord_list_enr[i][0]} {coord_list_enr[i][1]}",
                                             gml_id=enr_df.loc[i, 'gml_id'],
                                             identifier=enr_df.loc[i, 'identifier'],
                                             beginposition=enr_df.loc[i, 'beginPosition'],
                                             interpretation=enr_df.loc[i, 'interpretation'],
                                             sequencenumber=enr_df.loc[i, 'sequenceNumber'],
                                             correctionnumber=enr_df.loc[i, 'correctionNumber'],
                                             timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
                                             enr_df.loc[
                                                 i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
                                             name=enr_df.loc[i, 'name'],
                                             type=enr_df.loc[i, 'type'],
                                             lighted=enr_df.loc[i, 'lighted'],
                                             group=enr_df.loc[i, 'group'],
                                             verticalextent=enr_df.loc[i, 'verticalExtent'],
                                             verticalextent_uom=enr_df.loc[i, 'verticalExtent_uom'],
                                             timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=enr_df.loc[
                                                 i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
                                             designator=enr_df.loc[i, 'designator'],
                                             elevation=str(enr_df.loc[i, 'elevation']),
                                             elevation_uom=enr_df.loc[i, 'elevation_uom'],
                                             colour=enr_df.loc[i, 'colour'],
                                             geo=str(enr_df.loc[i, 'geometry']))
            db.session.add(enr_obstacles)
            db.session.commit()


for s in path_list_area_2:
    table = str(s)[61:65].replace('/', '_').replace('.gdb', '').lower() + "_Area2a_Obstacles"
    area_2a = geopandas.read_file(s, driver='OpenFileGDB')
    if area_2a.crs != 'EPSG:4326':
        area_2a = area_2a.to_crs('EPSG:4326')

    print(area_2a.columns)
    if 'Coordinate' not in area_2a.columns:
        area_2a.rename(columns={'Coordinates': 'Coordinate'}, inplace=True)

    for i in range(area_2a.shape[0]):
        if 'Shape_Length' not in area_2a.columns:
            area_2a.loc[i, 'Shape_Length'] = 0.0
        with app.app_context():
            area2a_obstacles = Area2aObstacles(aerodrome=table,
                                               obstacle_identifier=area_2a.loc[i, 'Obstacle_Identifier'],
                                               horizontal_accuracy=area_2a.loc[i, 'Horizontal_Accuracy'],
                                               horizontal_confidence_level=area_2a.loc[
                                                   i, 'Horizontal_Confidence_Level'],
                                               elevation=area_2a.loc[i, 'Elevation'],
                                               height=area_2a.loc[i, 'Height'],
                                               vertical_accuracy=area_2a.loc[i, 'Vertical_Accuracy'],
                                               vertical_confidence_level=area_2a.loc[
                                                   i, 'Vertical_Confidence_Level'],
                                               obstacle_type=area_2a.loc[i, 'Obstacle_Type'],
                                               integrity=area_2a.loc[i, 'Integrity'],
                                               date_and_time_stamp=str(area_2a.loc[i, 'Date_And_Time_Stamp']),
                                               operations=area_2a.loc[i, 'Operations'],
                                               effectivity=area_2a.loc[i, 'Effectivity'],
                                               lighting=area_2a.loc[i, 'Lighting'],
                                               marking=area_2a.loc[i, 'Marking'],
                                               horizontal_extent=area_2a.loc[i, 'Horizontal_Extent'],
                                               obstacle_name=area_2a.loc[i, 'Obstacle_Name'],
                                               marking_details=area_2a.loc[i, 'Marking_Details'],
                                               lighting_color=area_2a.loc[i, 'Lighting_Color'],
                                               coordinate=area_2a.loc[i, 'Coordinate'],
                                               shape_length=area_2a.loc[i, 'Shape_Length'],
                                               geo=str(area_2a.loc[i, 'geometry']))

            db.session.add(area2a_obstacles)
            db.session.commit()

for t in path_list_area_3:
    table = str(t)[69:73].replace('/', '_').replace('.gdb', '').lower() + "_Area3_Obstacles"
    area_3_df = geopandas.read_file(t, driver='OpenFileGDB')
    if area_3_df.crs != 'EPSG:4326':
        area_3_df = area_3_df.to_crs('EPSG:4326')



    for i in range(area_3_df.shape[0]):
        if 'Shape_Length' not in area_3_df.columns:
            area_3_df.loc[i, 'Shape_Length'] = 0.0
        with app.app_context():
            area3_obstacles = Area3Obstacles(aerodrome=table,
                                             obstacle_identifier=area_3_df.loc[i, 'Obstacle_Identifier'],
                                             horizontal_accuracy=area_3_df.loc[i, 'Horizontal_Accuracy'],
                                             horizontal_confidence_level=area_3_df.loc[
                                                 i, 'Horizontal_Confidence_Level'],
                                             elevation=area_3_df.loc[i, 'Elevation'],
                                             height=area_3_df.loc[i, 'Height'],
                                             vertical_accuracy=area_3_df.loc[i, 'Vertical_Accuracy'],
                                             vertical_confidence_level=area_3_df.loc[
                                                 i, 'Vertical_Confidence_Level'],
                                             obstacle_type=area_3_df.loc[i, 'Obstacle_Type'],
                                             integrity=area_3_df.loc[i, 'Integrity'],
                                             date_and_time_stamp=str(area_3_df.loc[i, 'Date_And_Time_Stamp']),
                                             operations=area_3_df.loc[i, 'Operations'],
                                             effectivity=area_3_df.loc[i, 'Effectivity'],
                                             lighting=area_3_df.loc[i, 'Lighting'],
                                             marking=area_3_df.loc[i, 'Marking'],
                                             horizontal_extent=area_3_df.loc[i, 'Horizontal_Extent'],
                                             obstacle_name=area_3_df.loc[i, 'Obstacle_Name'],
                                             marking_details=area_3_df.loc[i, 'Marking_Details'],
                                             lighting_color=area_3_df.loc[i, 'Lighting_Color'],
                                             coordinate=area_3_df.loc[i, 'Coordinate'],
                                             shape_length=area_3_df.loc[i, 'Shape_Length'],
                                             geo=str(area_3_df.loc[i, 'geometry']))

            db.session.add(area3_obstacles)
            db.session.commit()

"""
Area 3 LTAC Obstacles are in format of .mdb. To handle that https://fishcodelib.com/index.htm has a tool called
db.Migration.Net which converts .mdb to .sqlite. Then we can use geopandas to read the .sqlite file."""
""" Getting data from ltac_obstacles.db which is created from .mdb file. """
engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=False)

point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)

for i in range(point_df.shape[0]):
    point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
                                            float(point_df.loc[i, 'Coordinate'].split(' ')[1]))

point_gdf = geopandas.GeoDataFrame(point_df, geometry='GEOMETRY', crs='EPSG:4326')


line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
for i in range(line_df.shape[0]):
    line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))

line_gdf = geopandas.GeoDataFrame(line_df, geometry='GEOMETRY', crs='EPSG:4326')

polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)

for i in range(polygon_df.shape[0]):

    if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
        polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
        polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
    else:
        polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))

polygon_gdf = geopandas.GeoDataFrame(polygon_df, geometry='GEOMETRY', crs='EPSG:4326')


ltac_area3 = pd.concat([point_gdf, line_gdf, polygon_gdf], ignore_index=True)


""" Getting data from ltac_obstacles.db which is created from .mdb file. """

for w in range(ltac_area3.shape[0]):
    with app.app_context():
        ltac_area3_obstacles = LtacArea3Obstacles(Obstacle_Identifier=ltac_area3.loc[w, 'Obstacle_Identifier'],
                                                  Horizontal_Accuracy=ltac_area3.loc[w, 'Horizontal_Accuracy'],
                                                  Horizontal_Confidence_Level=ltac_area3.loc[
                                                      w, 'Horizontal_Confidence_Level'],
                                                  Elevation=ltac_area3.loc[w, 'Elevation'],
                                                  Height=ltac_area3.loc[w, 'Height'],
                                                  Vertical_Accuracy=ltac_area3.loc[w, 'Vertical_Accuracy'],
                                                  Vertical_Confidence_Level=ltac_area3.loc[
                                                      w, 'Vertical_Confidence_Level'],
                                                  Obstacle_Type=ltac_area3.loc[w, 'Obstacle_Type'],
                                                  Integrity=ltac_area3.loc[w, 'Integrity'],
                                                  Date_And_Time_Stamp=str(ltac_area3.loc[w, 'Date_And_Time_Stamp']),
                                                  Operations=ltac_area3.loc[w, 'Operations'],
                                                  Effectivity=ltac_area3.loc[w, 'Effectivity'],
                                                  Lighting=ltac_area3.loc[w, 'Lighting'],
                                                  Marking=ltac_area3.loc[w, 'Marking'],
                                                  Obstacle_Name=ltac_area3.loc[w, 'Obstacle_Name'],
                                                  Lighting_Color=ltac_area3.loc[w, 'Lighting_Color'],
                                                  Marking_Details=ltac_area3.loc[w, 'Marking_Details'],
                                                  Coordinate=ltac_area3.loc[w, 'Coordinate'],
                                                  SHAPE_Length=ltac_area3.loc[w, 'SHAPE_Length'],
                                                  SHAPE_Area=ltac_area3.loc[w, 'SHAPE_Area'],
                                                  Horizontal_Extent=ltac_area3.loc[w, 'Horizontal_Extent'],
                                                  geo=str(ltac_area3.loc[w, 'GEOMETRY']))

        db.session.add(ltac_area3_obstacles)
        db.session.commit()

for u in path_list_area_4:
    table = str(u)[69:].replace('/', '_').replace('.gdb', '').lower() + "_Area4_Obstacles"
    area_4_df = geopandas.read_file(u, driver='OpenFileGDB')
    if area_4_df.crs != 'EPSG:4326':
        area_4_df = area_4_df.to_crs('EPSG:4326')




    for i in range(area_4_df.shape[0]):
        if 'Shape_Length' not in area_4_df.columns:
                     area_4_df.loc[i, 'Shape_Length'] = 0.0
        if 'Shape_Area' not in area_4_df.columns:
            area_4_df.loc[i, 'Shape_Area'] = 0.0
        if 'Horizontal_Extent' not in area_4_df.columns:
            area_4_df.loc[i, 'Horizontal_Extent'] = 'NULL'

        if 'Coordinate' not in area_4_df.columns:
            area_4_df.rename(columns={'Coordinates':'Coordinate'}, inplace=True)
        with app.app_context():
                area4_obstacles = Area4Obstacles(aerodrome=table,
                                                 obstacle_identifier=area_4_df.loc[i, 'Obstacle_Identifier'],
                                                 horizontal_accuracy=area_4_df.loc[i, 'Horizontal_Accuracy'],
                                                 horizontal_confidence_level=area_4_df.loc[
                                                     i, 'Horizontal_Confidence_Level'],
                                                 elevation=area_4_df.loc[i, 'Elevation'],
                                                 height=area_4_df.loc[i, 'Height'],
                                                 vertical_accuracy=area_4_df.loc[i, 'Vertical_Accuracy'],
                                                 vertical_confidence_level=area_4_df.loc[
                                                     i, 'Vertical_Confidence_Level'],
                                                 obstacle_type=area_4_df.loc[i, 'Obstacle_Type'],
                                                 integrity=area_4_df.loc[i, 'Integrity'],
                                                 date_and_time_stamp=str(area_4_df.loc[i, 'Date_And_Time_Stamp']),
                                                 operations=area_4_df.loc[i, 'Operations'],
                                                 effectivity=area_4_df.loc[i, 'Effectivity'],
                                                 lighting=area_4_df.loc[i, 'Lighting'],
                                                 marking=area_4_df.loc[i, 'Marking'],
                                                 horizontal_extent=area_4_df.loc[i, 'Horizontal_Extent'],
                                                 obstacle_name=area_4_df.loc[i, 'Obstacle_Name'],
                                                 marking_details=area_4_df.loc[i, 'Marking_Details'],
                                                 lighting_color=area_4_df.loc[i, 'Lighting_Color'],
                                                 coordinate=area_4_df.loc[i, 'Coordinate'],
                                                 shape_length=area_4_df.loc[i, 'Shape_Length'],

                                                 geo=str(area_4_df.loc[i, 'geometry']))

                db.session.add(area4_obstacles)
                db.session.commit()


for j in path_list_area_4_xml:

    ltfm_area4_df = geopandas.read_file(j)
    if ltfm_area4_df.crs != 'EPSG:4326':
        ltfm_area4_df = ltfm_area4_df.to_crs('EPSG:4326')



    coord_list_ltfm = []
    coords = ltfm_area4_df.get_coordinates()
    for i in range(ltfm_area4_df.shape[0]):
        coord_list_ltfm.append([float(coords.loc[i].x), float(coords.loc[i].y)])
        with app.app_context():
            ltfm_area4_obstacles = LtfmArea4Obstacles(coordinate=f"{coord_list_ltfm[i][0]} {coord_list_ltfm[i][1]}",
                                                    gml_id=ltfm_area4_df.loc[i, 'gml_id'],
                                                    identifier=ltfm_area4_df.loc[i, 'identifier'],
                                                    beginposition=ltfm_area4_df.loc[i, 'beginPosition'],
                                                    interpretation=ltfm_area4_df.loc[i, 'interpretation'],
                                                    sequencenumber=ltfm_area4_df.loc[i, 'sequenceNumber'],
                                                    correctionnumber=ltfm_area4_df.loc[i, 'correctionNumber'],
                                                    timeslice_verticalstructuretimeslice_featurelifetime_timeperiod_beginposition=
                                                      ltfm_area4_df.loc[
                                                        i, 'timeSlice|VerticalStructureTimeSlice|featureLifetime|TimePeriod|beginPosition'],
                                                    name=ltfm_area4_df.loc[i, 'name'], type=ltfm_area4_df.loc[i, 'type'],
                                                    lighted=ltfm_area4_df.loc[i, 'lighted'],
                                                    group=ltfm_area4_df.loc[i, 'group'], verticalextent=ltfm_area4_df.loc[i, 'verticalExtent'],
                                                    verticalextent_uom=ltfm_area4_df.loc[i, 'verticalExtent_uom'],
                                                    timeslice_verticalstructuretimeslice_part_verticalstructurepart_type=ltfm_area4_df.loc[
                                                        i, 'timeSlice|VerticalStructureTimeSlice|part|VerticalStructurePart|type'],
                                                    designator=ltfm_area4_df.loc[i, 'designator'], elevation=ltfm_area4_df.loc[i, 'elevation'],
                                                    elevation_uom=ltfm_area4_df.loc[i, 'elevation_uom'], colour=ltfm_area4_df.loc[i, 'colour'],
                                                      geo=str(ltfm_area4_df.loc[i, 'geometry']))
            db.session.add(ltfm_area4_obstacles)
            db.session.commit()





