import folium
from flask import Flask, request, render_template_string, render_template, redirect
import matplotlib.pyplot as plt
import pandas as pd
import geopandas
import lxml
from folium.plugins import FastMarkerCluster
from flask_sqlalchemy import SQLAlchemy
from folium import Popup
from folium.plugins import MarkerCluster, FeatureGroupSubGroup, GroupedLayerControl
from geoalchemy2 import Geometry, Geography, Raster, RasterElement, WKBElement, CompositeElement, WKTElement
from sqlalchemy.orm import relationship
import rasterio
from rasterio.plot import show
import pyogrio
import dted
import numpy as np
from pathlib import Path
import sqlite3 as sq
from sqlalchemy import MetaData, create_engine
from flask_bootstrap import Bootstrap5
import shapely as shp

ad_list = ['LTAC', 'LTAF', 'LTAI', 'LTAJ', 'LTAN', 'LTAP', 'LTAR', 'LTAS', 'LTAT', 'LTAU', 'LTAW', 'LTAY', 'LTAZ',
           'LTBA', 'LTBD', 'LTBF', 'LTBH', 'LTBJ', 'LTBO', 'LTBQ', 'LTBR', 'LTBS', 'LTBU', 'LTBY', 'LTBZ', 'LTCA',
           'LTCB', 'LTCC', 'LTCD', 'LTCE', 'LTCF', 'LTCG', 'LTCI', 'LTCJ', 'LTCK', 'LTCL', 'LTCM', 'LTCN', 'LTCO',
           'LTCP', 'LTCR', 'LTCS', 'LTCT', 'LTCU', 'LTCV', 'LTCW', 'LTDA', 'LTFB', 'LTFC', 'LTFD', 'LTFE', 'LTFG',
           'LTFH', 'LTFJ', 'LTFK', 'LTFM', 'LTFO', ]
ad_df_list = ['LTAC_df', 'LTAF_df', 'LTAI_df', 'LTAJ_df', 'LTAN_df', 'LTAP_df', 'LTAR_df', 'LTAS_df', 'LTAT_df',
              'LTAU_df', 'LTAW_df', 'LTAY_df', 'LTAZ_df', 'LTBA_df', 'LTBD_df', 'LTBF_df', 'LTBH_df', 'LTBJ_df',
              'LTBO_df', 'LTBQ_df', 'LTBR_df', 'LTBS_df', 'LTBU_df', 'LTBY_df', 'LTBZ_df', 'LTCA_df', 'LTCB_df',
              'LTCC_df', 'LTCD_df', 'LTCE_df', 'LTCF_df', 'LTCG_df', 'LTCI_df', 'LTCJ_df', 'LTCK_df', 'LTCL_df',
              'LTCM_df', 'LTCN_df', 'LTCO_df', 'LTCP_df', 'LTCR_df', 'LTCS_df', 'LTCT_df', 'LTCU_df', 'LTCV_df',
              'LTCW_df', 'LTDA_df', 'LTFB_df', 'LTFC_df', 'LTFD_df', 'LTFE_df', 'LTFG_df', 'LTFH_df', 'LTFJ_df',
              'LTFK_df', 'LTFM_df', 'LTFO_df', ]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fea4877a6edb053d1acc1f7841d78dca98f2d5bab0af7220522cf94ef685bc2d'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aerodrome_obstacles.db'
# db = SQLAlchemy()
# db.init_app(app)
Bootstrap5(app)
path_list_ad = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles').rglob("*.xml"))
path_list_area_2 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
path_list_area_3 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_3_terrain_obstacles').rglob("*.gdb"))
path_list_area_4 = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles').rglob("*.gdb"))
path_list_area_4_xml = sorted(
    Path('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTFM_AREA_4').rglob("*.xml"))


def create_ad_obstacles_db(path_list):
    """
This function creates a database from .xml files for aerodrome obstacles for every airport in Turkey.
    :param path_list: Absolute path for every aerodrome obstacle xml file.
    """
    df = geopandas.read_file(path_list[1])
    for i in path_list:
        if path_list.index(i) == 0 or path_list.index(i) == 1:
            pass
        else:
            bdf = geopandas.read_file(i)
            df = pd.concat([df, bdf], ignore_index=True)

    df.to_file('aerodrome_obstacles.db', driver='SQLite')
create_ad_obstacles_db(path_list_ad)

def create_enr_obstacles_db():
    """
    This function creates a database from .xml file for AIP ENR 5.4 obstacles in Turkey.
    """
    df = geopandas.read_file('/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml')
    df.to_file('enr_obstacles.db', driver='SQLite')

create_enr_obstacles_db()
def read_ad_enr_obs_db(db_path):
    gdf = geopandas.read_file(db_path)
    return gdf

def read_area_3_4_db_alternate(path_list_ad,path_list_2,path_list_3,path_list_4, path_list_xml,maps):
    """
    This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
    LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
    WGS84. Also caution for file paths especially having space in it.

    """
    mcg = folium.plugins.MarkerCluster(control=False)
    maps.add_child(mcg)


    ydf = read_ad_enr_obs_db('/Users/dersim/PycharmProjects/mapping/enr_obstacles.db')
    g0 = folium.plugins.FeatureGroupSubGroup(mcg, 'En-route Obstacles')
    maps.add_child(g0)
    for y in range(ydf.shape[0]):
        coor = ydf.loc[y, 'geometry']
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
        marker = folium.Marker(location=[coor.y, coor.x], icon=icons)
        popup = (f"Elevation: {ydf.loc[y, 'elevation']} FT Type: {ydf.loc[y, 'type']} "
                 f" Coordinates: {coor.y}N, {coor.x}E")

        folium.Popup(popup).add_to(marker)
        marker.add_to(g0)



    for p in path_list_ad[1:]:
        layer_name = str(p)[64:78]
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ad_obstacles.db', echo=False)
        cdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')

        g1 = folium.plugins.FeatureGroupSubGroup(mcg, str(p)[64:68] + '_AD_Obst')
        maps.add_child(g1)
        for o in range(cdf.shape[0]):
            coor = cdf.get_coordinates(ignore_index=True)
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
            marker = folium.Marker(location=(coor.loc[o,'y'], coor.loc[o,'x']), icon=icons)
            popup = (f"Elevation: {cdf.loc[o, 'elevation']} FT Type: {cdf.loc[o, 'type']} "
                     f" Coordinates: {coor.loc[o,'y']}N, {coor.loc[o,'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g1)
    for n in path_list_2:
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area2a_obstacles.db', echo=False)
        layer_name = str(n)[61:].replace('/', '_').replace('.gdb', '').lower()
        bdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
        g2 = folium.plugins.FeatureGroupSubGroup(mcg, f'{str(n)[61:65]}' + '_Area2a_Obst')
        maps.add_child(g2)
        for o in range(bdf.shape[0]):
            coor = bdf.get_coordinates(ignore_index=True)
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
            marker = folium.Marker(location=(coor.loc[o,'y'], coor.loc[o,'x']), icon=icons)
            popup = (f"Elevation: {bdf.loc[o, 'elevation']} FT  Type: {bdf.loc[o, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[o,'y']}N, {coor.loc[o,'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g2)

    for i in path_list_3:
        layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area3_obstacles.db', echo=False)
        gdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
        g3 = folium.plugins.FeatureGroupSubGroup(mcg, str(i)[69:73] + '_Area3_Obst')
        maps.add_child(g3)
        for t in range(gdf.shape[0]):
            coor = gdf.get_coordinates(ignore_index=True)
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
            marker = folium.Marker(location=(coor.loc[t,'y'], coor.loc[t,'x']), icon=icons)
            popup = (f"Elevation: {gdf.loc[t, 'elevation']} FT  Type: {gdf.loc[t, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[t,'y']}N, {coor.loc[t,'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g3)
    layer_name = 'ltac_area_3_area_3'
    engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area3_obstacles.db', echo=False)
    zdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
    gx = folium.plugins.FeatureGroupSubGroup(mcg, 'LTAC' + '_Area3_Obst')
    maps.add_child(gx)
    for u in range(zdf.shape[0]):
        coor = zdf.get_coordinates(ignore_index=True)
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
        marker = folium.Marker(location=(coor.loc[u,'y'], coor.loc[u,'x']), icon=icons)
        popup = (f"Elevation: {zdf.loc[u, 'elevation']} FT  Type: {zdf.loc[u, 'obstacle_type']} "
                 f" Coordinates: {coor.loc[u,'y']}N, {coor.loc[u,'x']}E")

        folium.Popup(popup).add_to(marker)
        marker.add_to(gx)

    for j in path_list_4:
        layer_name = str(j)[69:].replace('/', '_').replace('.gdb', '').lower()
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
        hdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
        g4 = folium.plugins.FeatureGroupSubGroup(mcg,  str(j)[69:73] + '_Area4_Obst')
        maps.add_child(g4)

        for l in range(hdf.shape[0]):
            coor = hdf.get_coordinates(ignore_index=True)
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
            marker = folium.Marker(location=(coor.loc[l,'y'], coor.loc[l,'x']), icon=icons)
            popup = (f"Elevation: {hdf.loc[l, 'elevation']} FT  Type: {hdf.loc[l, 'obstacle_type']} "
                     f" Coordinates: {coor.loc[l,'y']}N, {coor.loc[l,'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g4)


    for k in path_list_xml:
        layer_name = str(k)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
        engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/area4_obstacles.db', echo=False)
        xdf = geopandas.read_postgis('SELECT * FROM ' + layer_name, con=engine, geom_col='GEOMETRY')
        g5 = folium.plugins.FeatureGroupSubGroup(mcg, str(k)[69:73] + 'Area4_Obstacles')
        maps.add_child(g5)
        for m in range(xdf.shape[0]):
            coor = xdf.get_coordinates(ignore_index=True)
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
            marker = folium.Marker(location=(coor.loc[m,'y'], coor.loc[m,'x']), icon=icons)
            popup = (f"Elevation: {xdf.loc[m, 'elevation']} FT  Type: {xdf.loc[m, 'type']}"
                     f" Coordinates: {coor.loc[m,'y']}N, {coor.loc[m,'x']}E")

            folium.Popup(popup).add_to(marker)
            marker.add_to(g5)

def create_area2a_db():
    """
    This function creates a database from .gdb files for area2a obstacles for every airport in Turkey. If data has crs type other
    than WGS84 transforms it to WGS84. Also caution for file paths especially having space in it.
    """
    path_list = sorted(Path('/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles').rglob("*.gdb"))
    for i in path_list:
        layer_name = str(i)[61:].replace('/', '_').replace('.gdb', '').lower()
        bdf = geopandas.read_file(i, driver='OpenFileGDB')
        if bdf.crs != 'EPSG:4326':
            bdf = bdf.to_crs('EPSG:4326')
        bdf.to_file('area2a_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)

create_area2a_db()
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


def create_area_3_4_db(path_list, area: int, path_list_xml):
    """
    This function creates a database from .gdb files for area3a and area4a obstacles for every airport other than
    LTFM. For LTFM we use the aixm format and different path. If data has crs type other than WGS84 transforms it to
    WGS84. Also caution for file paths especially having space in it.
    path_list: list of paths for .gdb files
    area: area number, 3 or 4
    path_list_xml: list of paths for .xml files which contains aerodrome data in it.
    """
    if area == 3:
        for i in path_list:
            layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
            bdf = geopandas.read_file(i, driver='OpenFileGDB')
            if bdf.crs != 'EPSG:4326':
                bdf = bdf.to_crs('EPSG:4326')
            bdf.to_file('area3_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)

    elif area == 4:
        for i in path_list:
            layer_name = str(i)[69:].replace('/', '_').replace('.gdb', '').lower()
            bdf = geopandas.read_file(i, driver='OpenFileGDB')
            if bdf.crs != 'EPSG:4326':
                bdf = bdf.to_crs('EPSG:4326')
            bdf.to_file('area4_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)

        for j in path_list_xml:
            layer_name = str(j)[69:].replace('/', '_').replace('_Obstacles_AIXM_5_1.xml', '').lower()
            bdf = geopandas.read_file(j)
            if bdf.crs != 'EPSG:4326':
                bdf = bdf.to_crs('EPSG:4326')
            bdf.to_file('area4_obstacles.db', driver='SQLite', spatialite=True, layer=layer_name)
    else:
        print('Wrong area number. Please enter 3 or 4.')
create_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
create_area_3_4_db(path_list_area_4, 4, path_list_area_4_xml)

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


# create_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
# create_area_3_4_db(path_list_area_4,4, path_list_area_4_xml)
area3_df = read_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
area_4_df = read_area_3_4_db(path_list_area_4, 4, path_list_area_4_xml)

geodf = read_ad_enr_obs_db('/Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db')

m_sample = folium.Map(location=[39, 35], zoom_start=6)
mk = MarkerCluster().add_to(m_sample)


def ad_marker_add(df, aerodrome, map):
    marker_cluster = MarkerCluster(
        name=aerodrome,
        overlay=True,
        control=True,
        icon_create_function=None
    )
    for i in range(df.shape[0]):
        coor = df.iloc[i].geometry
        icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png')
        marker = folium.Marker(location=[coor.y, coor.x], icon=icons)
        popup = (f"Elevation: {df.loc[i, 'elevation']} Type: {df.loc[i, 'type']} Name: {df.loc[i, 'name']}"
                 f" Coordinates: {coor.y}N, {coor.x}E")

        folium.Popup(popup).add_to(marker)
        marker_cluster.add_child(marker)

        marker_cluster.add_to(map)


@app.route("/")
def fullscreen():
    m = folium.Map(location=[39, 35], zoom_start=6)
    for ad in ad_list:
        ad_marker_add(geodf, ad, m)
    folium.LayerControl(collapsed=True).add_to(m)

    """Simple example of a fullscreen map."""
    folium.plugins.MousePosition().add_to(m)


    return m.get_root().render()


edf = read_ad_enr_obs_db('/Users/dersim/PycharmProjects/mapping/enr_obstacles.db')


@app.route("/enrobs")
def enr_obstacles():
    m2 = edf.explore(
        column='type',
        m=m_sample,
    )

    return m2.get_root().render()


@app.route("/iframe")
def iframe():
    """Embed a map as an iframe on a page."""
    m = folium.Map()

    # set the iframe width and height
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head></head>
                <body>
                    <h1>Using an iframe</h1>
                    {{ iframe|safe }}
                </body>
            </html>
        """,
        iframe=iframe,
    )


@app.route('/are2a')
def area_2a_obstacles():
    # Open DTED file using Rasterio
    dted_file_path1 = '/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles/LTAC_AREA_2A/R1_AREA_2A/Terrain/DTED/DTED2/E032/N40.DT2'
    dted_data = rasterio.open(dted_file_path1)
    dted_file_path2 = '/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles/LTAC_AREA_2A/R1_AREA_2A/Terrain/DTED/DTED2/E033/N40.DT2'
    dted_data2 = rasterio.open(dted_file_path2)
    dted_file_path3 = '/Users/dersim/PycharmProjects/mapping/aixm_/area2a_obstacles/LTAC_AREA_2A/R2_AREA_2A/Terrain/DTED/DTED2/E032/N40.DT2'
    dted_data3 = rasterio.open(dted_file_path3)
    dted_file_path4 = '/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTAC_AREA_4/R1_AREA_4_03L/Terrain/DTED/DTED2/E032/N40.DT2'
    dted_data4 = rasterio.open(dted_file_path4)

    attr = (
        'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')
    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    # Create a folium map centered on the data

    m3 = folium.Map(location=[dted_data.bounds.top, dted_data.bounds.left], zoom_start=6, tiles=tiles, attr=attr)

    # Plot the DTED data on the folium map
    folium.raster_layers.ImageOverlay(
        image=dted_data.read(1),  # Use the first band for visualization
        bounds=[[dted_data.bounds.bottom, dted_data.bounds.left], [dted_data.bounds.top, dted_data.bounds.right]],
        colormap=lambda x: (1, 0, 0, x),  # Adjust the colormap as needed
    ).add_to(m3)

    folium.raster_layers.ImageOverlay(
        image=dted_data2.read(1),  # Use the first band for visualization
        bounds=[[dted_data2.bounds.bottom, dted_data2.bounds.left], [dted_data2.bounds.top, dted_data2.bounds.right]],
        colormap=lambda x: (1, 0, 0, x),  # Adjust the colormap as needed
    ).add_to(m3)
    # folium.raster_layers.ImageOverlay(
    #     image=dted_data3.read(1),  # Use the first band for visualization
    #     bounds=[[dted_data3.bounds.bottom, dted_data3.bounds.left], [dted_data3.bounds.top, dted_data3.bounds.right]],
    #     colormap=lambda x: (1, 0, 0, x),  # Adjust the colormap as needed
    # ).add_to(m3)
    #
    # folium.raster_layers.ImageOverlay(
    #     image=dted_data4.read(1),  # Use the first band for visualization
    #     bounds=[[dted_data4.bounds.bottom, dted_data4.bounds.left], [dted_data4.bounds.top, dted_data4.bounds.right]],
    #     colormap=lambda x: (1, 0, 0, x),  # Adjust the colormap as needed
    # ).add_to(m3)

    # Display the map
    # m.save('map_with_dted.html')
    return m3.get_root().render()


@app.route('/area2a')
def real_2a():
    gdf = read_area2a()
    m4 = gdf.explore(column='obstacle_type', m=m_sample)

    return m4.get_root().render()


@app.route('/area3')
def area_3():
    hdf = read_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)

    m5 = hdf.explore(column='obstacle_type', m=m_sample)

    return m5.get_root().render()
engine = create_engine('sqlite:////Users/dersim/PycharmProjects/mapping/ltac_obstacles.db', echo=True)


point_df = pd.read_sql('SELECT * FROM Point_Obstacle', engine)

for i in range(point_df.shape[0]):
    point_df.loc[i, 'GEOMETRY'] = shp.Point(float(point_df.loc[i, 'Coordinate'].split(' ')[1]), float(point_df.loc[i, 'Coordinate'].split(' ')[1]))

point_gdf = geopandas.GeoDataFrame(point_df, geometry='GEOMETRY',crs='EPSG:4326')

def chunks(xs, n):
    n = max(1, n)
    return [tuple(xs[i:i + n]) for i in range(0, len(xs), n)]


line_df = pd.read_sql('SELECT * FROM Line_Obstacle', engine)
for i in range(line_df.shape[0]):
    line_df.loc[i, 'GEOMETRY'] = shp.LineString(chunks(line_df.loc[i, 'Coordinate'].split(' '), 2))



line_gdf = geopandas.GeoDataFrame(line_df, geometry='GEOMETRY',crs='EPSG:4326')

polygon_df = pd.read_sql('SELECT * FROM Poligon_Obstacle', engine)
for i in range(polygon_df.shape[0]):

    if len(polygon_df.loc[i, 'Coordinate'].split(' ')) % 2 != 0:
        polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' ').pop(), 2))
    else:
        polygon_df.loc[i, 'GEOMETRY'] = shp.Polygon(chunks(polygon_df.loc[i, 'Coordinate'].split(' '), 2))

polygon_gdf = geopandas.GeoDataFrame(polygon_df, geometry='GEOMETRY',crs='EPSG:4326')
ltac_gdf = pd.concat([point_gdf, line_gdf, polygon_gdf], ignore_index=True)
@app.route('/area4')
def area_4():
    idf = read_area_3_4_db(path_list_area_4, 4, path_list_area_4_xml)
    m6 = idf.explore(column='elevation',m=m_sample)
    aqdf = geopandas.GeoDataFrame(line_df, geometry='GEOMETRY', crs='EPSG:4326')
    mapa = folium.Map(location=[39, 35], zoom_start=6)
    for i in range(aqdf.shape[0]):
        folium.PolyLine(locations=aqdf.loc[i, 'GEOMETRY'].coords[:], color='red').add_to(mapa)


    return mapa.get_root().render()


def marker_add(geodata, feature_g,feature_g1, maps):
    loc = []

    marker_cluster = MarkerCluster(

        control=False
    )
    maps.add_child(marker_cluster)
    g = FeatureGroupSubGroup(marker_cluster, feature_g)
    maps.add_child(g)

    coordinates = geodata.get_coordinates(ignore_index=True)

    for i in coordinates.index:
        loc.append((coordinates.loc[i, 'y'], coordinates.loc[i, 'x']))

    for k in range(geodata.shape[0]):
        marker = folium.Marker(location=loc[k])
        popup = f'Elevation: {geodata.loc[k, "elevation"]} \n Coordinates: {loc[k][0]}N, {loc[k][1]}E'
        icon_image = '/Users/dersim/PycharmProjects/mapping/icons/marker_dot.png'

        folium.CustomIcon(icon_image=icon_image, icon_size=(8, 8)).add_to(marker)
        folium.Popup(popup).add_to(marker)
        marker.add_to(g)




@app.route('/all')
def all():
    # kw = {"prefix": "fa", "color": "#0061ff", "icon": "circle"}
    # icons = folium.Icon(**kw)
    aerodrome_obstacles_df = read_ad_enr_obs_db('/Users/dersim/PycharmProjects/mapping/aerodrome_obstacles.db')
    enr_obstacles_df = read_ad_enr_obs_db('/Users/dersim/PycharmProjects/mapping/enr_obstacles.db')
    area2a_obstacles_df = read_area2a()
    area3_df = read_area_3_4_db(path_list_area_3, 3, path_list_area_4_xml)
    area_4_df = read_area_3_4_db(path_list_area_4, 4, path_list_area_4_xml)

    m7 = folium.Map(location=[39, 35], zoom_start=6, column='type', cmap='terrain')

    fg_ad = 'Aerodrome Obstacles'
    fg_enr = 'En-route Obstacles'
    fg_a2a = 'Area 2a Obstacles'
    fg_a3 = 'Area 3  Obstacles'
    fg_a4 = 'Area 4 Obstacles'
    fg_ad1 = folium.FeatureGroup(name='Aerodrome Obstacles')
    fg_enr1 = folium.FeatureGroup(name='En-route Obstacles')
    fg_a2a1 = folium.FeatureGroup(name='Area 2a Obstacles')
    fg_a31 = folium.FeatureGroup(name='Area 3  Obstacles')
    fg_a41 = folium.FeatureGroup(name='Area 4 Obstacles')

    marker_add(aerodrome_obstacles_df, fg_ad,fg_ad1, m7)
    marker_add(enr_obstacles_df, fg_enr, fg_enr1, m7)
    marker_add(area2a_obstacles_df, fg_a2a, fg_a2a1, m7)
    marker_add(area3_df, fg_a3, fg_a31, m7)
    marker_add(area_4_df, fg_a4, fg_a41, m7)
    folium.LayerControl(collapsed=False).add_to(m7)

    # locations = []
    # for i in range(enr_obstacles_df.shape[0]):
    #     print(type(enr_obstacles_df.loc[i, 'geometry']))
    #     print(enr_obstacles_df.loc[i, 'geometry'])
    #     coordinates = enr_obstacles_df.loc[i, 'geometry'].coords[:]
    #     for j in coordinates:
    #         locations.append(j)
    #
    # for i in locations:
    #     folium.Marker(location=i[::-1], icon=icons).add_to(mkk)

    return m7.get_root().render()


# @app.route("/components")
# def components():
#     """Extract map components and put those on a page."""
#     m = folium.Map(
#         width=800,
#         height=600,
#     )
#     edf.explore(m=m)
#
#     m.get_root().render()
#     header = m.get_root().header.render()
#     body_html = m.get_root().html.render()
#     script = m.get_root().script.render()
#
#     return render_template_string(
#         """
#             <!DOCTYPE html>
#             <html>
#                 <head>
#                     {{ header|safe }}
#                 </head>
#                 <body>
#                     <h1>Using components</h1>
#                     {{ body_html|safe }}
#                     <script>
#                         {{ script|safe }}
#                     </script>
#                 </body>
#             </html>
#         """,
#         header=header,
#         body_html=body_html,
#         script=script)
@app.route("/component")
def components():
    """Extract map components and put those on a page."""
    m = folium.Map(width=1140, height=600, location=[39, 35], zoom_start=6)
    edf.explore(m=m,
                column='elevation',
                tooltip=['name', 'type', 'elevation', 'elevation_uom', 'verticalextent', 'verticalextent_uom',
                         'lighted', 'GEOMETRY'],
                cmap='terrain')
    folium.plugins.MousePosition().add_to(m)
    m.get_root().render()
    # header = m.get_root().header.render()
    body_html = m.get_root().render()
    # script = m.get_root().script.render()

    return render_template('map.html', body_html=body_html)

@app.route('/all_2')
def all_2():
    mall = folium.Map(location=[39, 35], zoom_start=6)
    read_area_3_4_db_alternate(path_list_ad, path_list_area_2, path_list_area_3, path_list_area_4, path_list_area_4_xml,mall)
    folium.LayerControl(collapsed=False).add_to(mall)
    return mall.get_root().render()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
