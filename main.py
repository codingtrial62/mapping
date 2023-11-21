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
import dted
import numpy as np
from pathlib import Path



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
df = geopandas.read_file('/Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles/LTAC_Obstacles/LTAC_Obstacles_AIXM_5_1.xml',engine='pyogrio')

for i in range(1, len(ad_list)):
    ad_df_list[i] = geopandas.read_file(
        f'//Users/dersim/PycharmProjects/mapping/aixm_/aerodrome obstacles/{ad_list[i]}_Obstacles/{ad_list[i]}_Obstacles_AIXM_5_1.xml')
    df = pd.concat([df, ad_df_list[i]], ignore_index=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fea4877a6edb053d1acc1f7841d78dca98f2d5bab0af7220522cf94ef685bc2d'
#
#
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///obstacles.db'
# # db = SQLAlchemy()
# # db.init_app(app)
#
@app.route("/")
def fullscreen():
    m = folium.Map(location=[39, 35], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)
    for i in range(df.shape[0]):
        if 'BUILDING' in df.loc[i, 'name'] or 'BULDING' in df.loc[i, 'name']:
            # kw = {"prefix": "fa", "color": "green", "icon": "building"}
            # icons = folium.Icon(**kw)
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/building.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif 'MAST' in df.loc[i, 'name']:
            if df.loc[i, 'name'] == 'LIGHTING MAST':
                # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
                # icons = folium.Icon(**kw)
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/street-light.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'APRON LIGHTING MAST' or df.loc[i, 'name'] == 'APRON LIGTHING MAST':
                # kw = {"prefix": "fa", "color": "red", "icon": "shower"}
                # icons = folium.Icon(**kw)
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/apron_lighting.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            else:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/mast.png')
                # folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/aixm_mapping/icons8-pylon-64.png')
                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)


        elif df.loc[i, 'name'] == 'MOSQUE' or df.loc[i, 'name'] == 'MOSQUE_DOME':

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/mosque.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'MINARET':

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/minaret.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif 'SURVEILLANCE TOWER' in df.loc[i, 'name'] or 'TWR' in df.loc[i, 'name']:
            kw = {"prefix": "fa", "color": "pink", "icon": "tower-observation"}
            icons = folium.Icon(**kw)

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif 'ANTENNA' in df.loc[i, 'name']:
            if df.loc[i, 'name'] == 'GSM ANTENNA':
                kw = {"prefix": "fa", "color": "purple", "icon": "signal"}
                icons = folium.Icon(**kw)
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gsm_anten.png')
                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)

            elif df.loc[i, 'name'] == 'DME ANTENNA' or df.loc[i, 'name'] == 'DME ANTENNA(GP)':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/dme_antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'GLIDE PATH  ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA' \
                    or df.loc[i, 'name'] == 'GP ANTENNA' or df.loc[i, 'name'] == 'GLIDE PATH ANTENNA':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/glidepath_antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'LLZ ANTENNA':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/llz_ant.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'NDB ANTENNA':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/ndb_antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'TACAN ANTENNA':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tacan_antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'VOR ANTENNA':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor_antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
            elif df.loc[i, 'name'] == 'NF ANTENNA':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/nf_antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)

            else:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/antenna.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)
        elif df.loc[i, 'name'] == 'CHIMNEY' or df.loc[i, 'name'] == 'SHAFT':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/chimney.png')

            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ANM' or 'ANEMO' in df.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/anemometer.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif 'WIND' in df.loc[i, 'name']:
            if 'DIRECTION' in df.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-direction.png')
                coor = df.loc[i, 'geometry']
                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)


            elif 'ROSE' in df.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-rose.png')
                coor = df.loc[i, 'geometry']
                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)

            elif 'TURBINE' in df.loc[i, 'name'] or 'T' in df.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-turbine.png')
                coor = df.loc[i, 'geometry']
                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)

            else:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/windsock.png')
                coor = df.loc[i, 'geometry']
                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
                ).add_to(marker_cluster)

        elif 'WDI' in df.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-direction.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif 'APPROACH' in df.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/landing-track.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif 'POLE' in df.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/pole.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'LIGHTNING ROD' or df.loc[i, 'name'] == 'PARATONER' or df.loc[
            i, 'name'] == 'PARATONNERRE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/lightning-rod.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'HOSPITAL':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/hospital.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'DME' or df.loc[i, 'name'] == 'DME ILS/GP':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/dme.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'NDB':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/ndb.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'TACAN' or df.loc[i, 'name'] == 'TACAN CONTAINER':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tacan.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'VOR' or df.loc[i, 'name'] == 'VOR CONTAINER' or df.loc[i, 'name'] == 'VOR STATION':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'VOR+DME' or df.loc[i, 'name'] == 'VOR/DME':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vor_dme.png')
            coor = df.loc[i, 'geometry']
            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/nf_antenna.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif 'LIGHT' in df.loc[i, 'name']:

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/street-light.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'GREENHOUSE' or df.loc[i, 'name'] == 'GREEN HOUSE' or df.loc[
            i, 'name'] == 'PLANT-HOUSE' or df.loc[i, 'name'] == 'GARDEN FRAME':

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/greenhouse.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif df.loc[i, 'name'] == 'SILO' or df.loc[i, 'name'] == 'GRAIN SILO':

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/silo.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'STADIUM':

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/stadium.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif 'HOOK BARRIER' in df.loc[i, 'name']:

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/hook.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif 'NET BARRIER' in df.loc[i, 'name']:

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/net.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'CONCRETE BARRIER' or df.loc[i, 'name'] == 'CONCRETE BLOCK' or df.loc[
            i, 'name'] == 'BETON BARIYER':

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/concrete_barrier.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif 'WALL' in df.loc[i, 'name']:

            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wall.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ATC1_AERIAL' or df.loc[i, 'name'] == 'ATC2_AERIAL':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/nf_antenna.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif (df.loc[i, 'name'] == 'DVOR' or df.loc[i, 'name'] == 'DVOR_LC' or df.loc[i, 'name'] == 'DVOR_MONITOR'
              or df.loc[i, 'name'] == 'FFM_18' or df.loc[i, 'name'] == 'FFM_17L' or df.loc[i, 'name'] == 'FFM-35R'
              or df.loc[i, 'name'] == "FFM_34L" or df.loc[i, 'name'] == 'FFM_36' or df.loc[i, 'name'] == 'GLIDE PATH'
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
              or df.loc[i, 'name'] == 'LLZ CONTAINER' or df.loc[i, 'name'] == 'LLZ16' or df.loc[i, 'name'] == 'LLZ_18'
              or df.loc[i, 'name'] == 'RVR' or df.loc[i, 'name'] == 'PAPI_COVER' or df.loc[i, 'name'] == 'LOCALIZER' or
              df.loc[i, 'name'] == 'RAPCON'
              or df.loc[i, 'name'] == 'RVR-SENSOR') or df.loc[i, 'name'] == 'NDB FIELD' or df.loc[i, 'name'] == 'GCA' or \
                df.loc[i, 'name'] == 'SENTRY BOX' \
                or df.loc[i, 'name'] == 'NFM_34L':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/other_navigation_aid.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)
        elif df.loc[i, 'name'] == 'GSM BASE STATION' or df.loc[i, 'name'] == 'GSM STATION':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gsm_anten.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'GAS STATION':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gas-station.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'RADAR_STATION':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/radar.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif (df.loc[i, 'name'] == 'CABIN' or df.loc[i, 'name'] == 'CONSTRUCTION' or df.loc[i, 'name'] == 'COTTAGE'
              or df.loc[i, 'name'] == 'GUARD COTTAGE' or df.loc[i, 'name'] == 'STRUCTURE'):
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/cabin.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'HANGAR':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/hangar.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'MILITARY TRENCH':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/trench.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'REFLECTOR':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/reflector.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ROCK' or df.loc[i, 'name'] == 'STACK' \
                or df.loc[i, 'name'] == 'CLIFF':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/rock_stack_cliff.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'TREE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tree.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'VAN CASTLE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/castle.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'BRIDGE_DECK':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/bridge_deck.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'TRANSFORMER':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/transformer.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'TRAFFIC_SIGN' or df.loc[i, 'name'] == 'TRAFFIC BOARD' \
                or df.loc[i, 'name'] == 'SIGNBOARD':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/sign_board.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'PYLON':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/pylon.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'CRANE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/crane.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ARFF POOL':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/arff_pool.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ENERGY TRANSMISSION LINE' or df.loc[i, 'name'] == 'POWER_TRANSMISSION_LINE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/transmission.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'CONTAINER':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/container.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif 'TERRAIN' in df.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/terrain.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'BASE STATION':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/base_station.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'BILLBOARD':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/billboard.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'CAMERA PANEL':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/panel.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'FENCE' or df.loc[i, 'name'] == 'WIRE FENCE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/fence.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'FUEL_TANK':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/fuel_tank.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'WATER TANK':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/water_tank.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'WATER ROSERVOIR':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/reservoir.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'ENERGY CABIN':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/energy_cabin.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'METEOROLOGY DEVICE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/meteo_device.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'OKIS':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/okis.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'TERMINAL':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/terminal.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'VOICE BIRD SCARING SYSTEM':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/vbss.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'WATCH BOX':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/watch_box.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)

        elif df.loc[i, 'name'] == 'GNSS_MEASUREMENT_POINT':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gnss.png')

            coor = df.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{df.loc[i, 'elevation']} Designator:{df.loc[i, 'designator']} Type:{df.loc[i, 'type']} Name:{df.loc[i, 'name']}")
            ).add_to(marker_cluster)


        else:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/laughing.png')

            folium.Marker(
                location=[39, 35], icon=icons, popup=Popup('AMK')
            ).add_to(marker_cluster)
    """Simple example of a fullscreen map."""

    return marker_cluster.get_root().render()


edf = geopandas.read_file(
    '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml')


@app.route("/enrobs")
def enr_obstacles():
    m2 = folium.Map(location=[39, 35], zoom_start=6)
    marker_cluster2 = MarkerCluster().add_to(m2)
    for i in range(edf.shape[0]):
        if 'WIND' in edf.loc[i, 'name']:
            if 'MAST' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind_measure.png')

                coor = df.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)
            else:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/wind-farm.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

        elif 'ANTENNA' in edf.loc[i, 'name']:
            if 'MAST' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tv-tower.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

            else:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/antenna.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

        elif 'BRIDGE' in edf.loc[i, 'name']:
            if 'TOWER' and 'LINE' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/bridge_tower_line.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

            elif 'TOWER' and 'CABLE' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/bridge_tower.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

            elif 'TOWER' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/bridge_tower2.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

            elif 'ABUTMENT' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/abutment.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

            elif 'ROPE' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/rope_bridge.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

            elif 'MAST' in edf.loc[i, 'name']:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/bridge_mast.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)

        elif 'ABUTMENT' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/abutment.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'TORCH' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/torch_mast.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'TRANSMITTER' in edf.loc[i, 'name']:
            if edf.loc[i, 'name'] == 'CAMLICA TV TRANSMITTER':
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/camlica_tv.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)
            else:
                icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tv_transmitter.png')

                coor = edf.loc[i, 'geometry']

                folium.Marker(
                    location=[coor.y, coor.x], icon=icons, popup=Popup(
                        f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
                ).add_to(marker_cluster2)
        elif 'FLAG' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/flag_turkey.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'GSM' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/gsm_tower.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'TOWER CRANE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tower_crane.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'CRANE':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/crane.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'CHIMNEY':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/chimney.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'BUILDING':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/building.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'MINARET':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/minaret.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'DAM':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/dam.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'BALOON' in edf.loc[i, 'name'] or 'BALLOON' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/weather-balloon.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'ELECTRICITY' in edf.loc[i, 'name'] or 'ENERGY' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/power-line.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'RADIO LINK TOWER' or edf.loc[i, 'name'] == 'RADIO/TV LINE MAST':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/radio_tower.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'TELEPHONE/TELEGRAPH LINE MAST' in edf.loc[i, 'name'] :
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/telegraph.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'ZIPLINE' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/zipline.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'TOWER' or edf.loc[i, 'name'] == 'T':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/tower-block.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif 'ERZINCAN STEEL LINE' in edf.loc[i, 'name']:
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/steel_line.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

        elif edf.loc[i, 'name'] == 'OTHER':
            icons = folium.CustomIcon(icon_image='/Users/dersim/PycharmProjects/mapping/icons/other_obs.png')

            coor = edf.loc[i, 'geometry']

            folium.Marker(
                location=[coor.y, coor.x], icon=icons, popup=Popup(
                    f"Elevation:{edf.loc[i, 'elevation']} FT Designator:{edf.loc[i, 'designator']} Type:{edf.loc[i, 'type']} Name:{edf.loc[i, 'name']}")
            ).add_to(marker_cluster2)

    return marker_cluster2.get_root().render()


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



    attr = ('Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')
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
    folium.raster_layers.ImageOverlay(
        image=dted_data3.read(1),  # Use the first band for visualization
        bounds=[[dted_data3.bounds.bottom, dted_data3.bounds.left], [dted_data3.bounds.top, dted_data3.bounds.right]],
        colormap=lambda x: (1, 0, 0, x),  # Adjust the colormap as needed
    ).add_to(m3)

    folium.raster_layers.ImageOverlay(
        image=dted_data4.read(1),  # Use the first band for visualization
        bounds=[[dted_data4.bounds.bottom, dted_data4.bounds.left], [dted_data4.bounds.top, dted_data4.bounds.right]],
        colormap=lambda x: (1, 0, 0, x),  # Adjust the colormap as needed
    ).add_to(m3)





    # Display the map
    #m.save('map_with_dted.html')
    return m3.get_root().render()

@app.route('/area2a')
def real_2a():

    gdb_file =geopandas.read_file('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTAC_AREA_4/R1_AREA_4_03L/R1 Area4 03L.gdb', driver='OpenFileGDB')
    m4 = gdb_file.geometry.explore()


    return m4.get_root().render()

@app.route("/components")
def components():
    """Extract map components and put those on a page."""
    m = folium.Map(
        width=800,
        height=600,
    )

    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>Using components</h1>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script)


if __name__ == '__main__':
    app.run(debug=True)
# edf = geopandas.read_file(
#     '/Users/dersim/PycharmProjects/mapping/aixm_/ENR 5.4 Obstacles/LT_ENR_5_4_Obstacles_AIXM_5_1.xml')


gdb_file =geopandas.read_file('/Users/dersim/PycharmProjects/mapping/aixm_/area_4_terrain_obstacles/LTAC_AREA_4/R1_AREA_4_03L/R1 Area4 03L.gdb', driver='OpenFileGDB')
print(gdb_file.columns)