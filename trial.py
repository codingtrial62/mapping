
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
secret_key = os.environ.get('SECRET_KEY')
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key


path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_to_enr = '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml'
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ltac_obstacles.db'
db = SQLAlchemy()
db.init_app(app)
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

with app.app_context():
    result = db.session.execute(db.select(Point_Obstacle))
    user = result.scalar()
    print(point_df)

    for i in range(point_df.shape[0]):
        point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[0]),
                                                float(point_df.loc[i, 'Coordinate'].split(' ')[1]))

    point_gdf = geopandas.GeoDataFrame(point_df, geometry='GEOMETRY', crs='EPSG:4326')

    line_df = db.session.query(text('SELECT * FROM Line_Obstacle'))
    for i in range(line_df.shape[0]):
        line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))

    line_gdf = geopandas.GeoDataFrame(line_df, geometry='GEOMETRY', crs='EPSG:4326')

    polygon_df = db.session.query(text('SELECT * FROM Poligon_Obstacle'))
    for i in range(polygon_df.shape[0]):

        if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
            polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
            polygon_df.loc[i, 'Coordinate'] = polygon_df.loc[i, 'Coordinate'][:-1]
        else:
            polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))

    polygon_gdf = geopandas.GeoDataFrame(polygon_df, geometry='GEOMETRY', crs='EPSG:4326')



@app.route('/aqi')
def trial():
    maps = folium.Map(location=[39,35], zoom_start=6,)
    mcg = folium.plugins.MarkerCluster(control=False)
    maps.add_child(mcg)
    g6 = folium.plugins.FeatureGroupSubGroup(mcg, 'LTAC_Area3_Obst')
    maps.add_child(g6)
    for e in range(line_df.shape[0]):
        folium.PolyLine(locations=chunks2(line_df.loc[e, 'Coordinate'].split(' '), 2), color='red',
                        popup=f"Elevation: {line_df.loc[e, 'Elevation']} FT  Type: {line_df.loc[e, 'Obstacle_Type']} "
                              f" Coordinates(..N..E): {chunks2(line_df.loc[e, 'Coordinate'].split(' '), 2)}").add_to(g6)

    for w in range(polygon_df.shape[0]):
        folium.Polygon(locations=chunks2(polygon_df.loc[w, 'Coordinate'].split(' '), 2), color='red',
                       popup=f"Elevation: {polygon_df.loc[w, 'Elevation']} FT  Type: {polygon_df.loc[w, 'Obstacle_Type']} "
                             f" Coordinates(..N..E): {chunks2(polygon_df.loc[w, 'Coordinate'].split(' '), 2)}").add_to(
            g6)

    for c in range(point_gdf.shape[0]):
        coords = point_gdf.loc[c, 'GEOMETRY']
        icon_images = '/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png'
        folium.Marker(location=[coords.x, coords.y],
                      icon=folium.CustomIcon(icon_image=icon_images, icon_size=(8, 8)), color='red',
                      popup=f"Elevation: {point_gdf.loc[c, 'Elevation']} Type: {point_gdf.loc[c, 'Obstacle_Type']} "
                            f" Coordinates: {coords.y}N, {coords.x}E").add_to(g6)

    frame = maps.get_root()._repr_html_()
    return render_template('mapping.html', frame=frame)


if __name__ == '__main__':
    app.run(debug=True, port=5001)