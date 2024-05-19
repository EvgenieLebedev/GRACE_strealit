import streamlit as st
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import datetime
import warnings
import requests
from io import BytesIO

warnings.filterwarnings('ignore')

st.title("Визуализация данных GRACE")
st.write("Этот проект выполнен Лебедевым Е.Д. в рамках магистерской ВКР по исследованию поля силы тяжести")


def no_hash(obj):
    return None

@st.cache_resource(hash_funcs={Dataset: no_hash})
def download_data(url):
    anser = requests.get(url, allow_redirects=True)
    print(anser.status_code)
    r = requests.get(url, allow_redirects=True).content
    return Dataset("name", memory=r)

@st.cache_data
def process_data(_data):
    lats = _data.variables['lat'][:]
    lons = _data.variables['lon'][:]
    time = _data.variables['time'][:]
    lwe = _data.variables['lwe_thickness'][:]
    
    time_days = [(datetime.datetime(2002, 1, 1, 0, 0) + datetime.timedelta(days=int(i))).strftime("%Y-%m-%d") for i in time]
    
    f = lambda x: ((x + 180) % 360) - 180
    tmprt_lon = f(lons)
    ind = np.argsort(tmprt_lon)

    lons = tmprt_lon[ind]
    lwe = lwe[:, :, ind]
    
    return lats, lons, time_days, lwe

st.write('Загрузка данных...')
url = "http://download.csr.utexas.edu/outgoing/grace/RL0602_mascons/CSR_GRACE_GRACE-FO_RL0602_Mascons_all-corrections.nc"
data = download_data(url)
st.write('Данные загружены!')

lats, lons, time_days, lwe = process_data(data)

time_val = st.selectbox('Выберите месяц', time_days)
bounds_val = st.selectbox('Выберите масштаб', [15, 20, 25, 30, 50, 100, 500])
cmap_val = st.selectbox('Выберите цветовую схему', ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'])

fig, ax = plt.subplots(figsize=(11, 4))

mp = Basemap(projection='robin', resolution='i', lon_0=0, lat_0=0, ax=ax)

lon, lat = np.meshgrid(lons, lats)
x, y = mp(lon, lat)

mp.drawcoastlines()

month_num = time_days.index(time_val)
c_scheme = mp.pcolormesh(x, y, np.squeeze(lwe[month_num, :, :]), cmap=cmap_val, vmin=-bounds_val, vmax=bounds_val)
# cbar = mp.colorbar(c_scheme, location='right', pad='10%')
ax.set_title(f'Данные GRACE за {time_val}')

st.pyplot(fig)
