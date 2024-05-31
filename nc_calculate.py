import streamlit as st
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cmocean
import boule as bl

def minmax(data, fields):
    """
    Получает минимальные и максимальные значения данных для всех заданных полей.
    Возвращает их в словаре с ключами 'vmin' и 'vmax'.
    """
    vmin = min(data[field].min() for field in fields)
    vmax = max(data[field].max() for field in fields)
    return dict(vmin=vmin, vmax=vmax)

# Загрузка набора данных
data = xr.open_dataset('./Gravity/hawaii-gravity.nc')

# Функция для построения графиков
def plot_hawaii_data(data, field, **kwargs):
    fig = plt.figure(figsize=(12, 13))
    ax = plt.axes(projection=ccrs.PlateCarree())
    plot_field(ax, data, field, **kwargs)
    st.pyplot(fig)

# Функция для построения поля
def plot_field(ax, data, field, **kwargs):
    data[field].plot(ax=ax, transform=ccrs.PlateCarree(), **kwargs)
    ax.coastlines()

# Расчет возмущения гравитационного поля
ellipsoid = bl.WGS84
data['normal_gravity'] = ellipsoid.normal_gravity(data.latitude, data.h_over_ellipsoid)
data['gravity_disturbance'] = data.gravity_earth - data['normal_gravity']

# Интерфейс для изменения границ цветовой шкалы
def crop_colorbar(cutoff):
    vmin, vmax = -cutoff, cutoff
    plot_hawaii_data(data, 'gravity_disturbance', cmap='RdBu_r', vmin=vmin, vmax=vmax)

# Бугеррская поправка
G = 6.67430e-11  # Гравитационная постоянная в м^3 кг^-1 с^-2
density = 2670.0  # Плотность пластины Буге в кг/м^3
data['bouguer_plate_correction'] = 2 * np.pi * G * density * data['topography_grd'] * 1e5  # преобразование из м/с^2 в mGal
data['gravity_bouguer'] = data['gravity_disturbance'] - data['bouguer_plate_correction']

# Словарь переводов
field_labels = {
    'gravity_disturbance': 'Потенциал силы тяжести',
    'gravity_bouguer': 'Редукция Бурге',
    'topography_ell': 'Топография'
}

# Класс для выбора профиля
class ProfileSelector:
    def __init__(self, data, fields, projection, figsize=(15, 9), profile_interval=10, dimension='latitude'):
        self.data = data
        self.fields = fields
        self.projection = projection
        self.figsize = figsize
        self.profile_interval = profile_interval
        self.default_dimension = dimension
        self._plot_initiated = False

    def plot(self, location, dimension):
        if not self._plot_initiated:
            self.fig = plt.figure(figsize=self.figsize)
            grid = plt.GridSpec(2, 4, hspace=0, wspace=0)
            self.ax_data = self.fig.add_subplot(grid[0, :-1])
            self.ax_topo = self.fig.add_subplot(grid[1, :-1])
            self.ax_data_map = self.fig.add_subplot(grid[0, -1], projection=self.projection)
            self.ax_topo_map = self.fig.add_subplot(grid[1, -1], projection=self.projection)

            self._topo_base = -10000
            ylim_topo = [self._topo_base, self.data.topography_ell.max() * 1.1]
            ylim_data = list(sorted(minmax(self.data, self.fields).values()))

            self.ax_data.set_ylim(ylim_data)
            self.ax_data.set_ylabel('mGal')
            self.ax_topo.set_ylim(ylim_topo)
            self.ax_topo.set_ylabel('Топография (м)')
            self.ax_data.grid(True)
            self.ax_data.set_xticklabels([])

            self._data_lines = {field: self.ax_data.plot([0], [0], '-', label=field_labels.get(field, field))[0] for field in self.fields}
            self.ax_data.legend(loc='upper right')

            self._water_fill = None
            self._topo_fill = None

            plot_field(self.ax_data_map, self.data, self.fields[0], cmap='RdBu_r')
            plot_field(self.ax_topo_map, self.data, 'topography_ell', cmap=cmocean.cm.delta)

            self._datamap_profile = self.ax_data_map.plot([0, 0], [0, 0], '--k')[0]
            self._topomap_profile = self.ax_topo_map.plot([0, 0], [0, 0], '--k')[0]

            plt.tight_layout(pad=0, h_pad=0, w_pad=0)
            self._plot_initiated = True

        dim_comp = set(self.data.dims).difference({dimension}).pop()
        x = self.data[dimension]
        xlim = [x.min(), x.max()]
        profile = self.data.loc[{dim_comp: location}]

        for field in self.fields:
            self._data_lines[field].set_data(x, profile[field])

        if self._topo_fill is not None:
            self._topo_fill.remove()
        if self._water_fill is not None:
            self._water_fill.remove()
        self._water_fill = self.ax_topo.fill_between(xlim, [0, 0], self._topo_base, color='#2780E3')
        self._topo_fill = self.ax_topo.fill_between(x, profile.topography_ell, self._topo_base, color='#333333')

        profile_location = [xlim, [location, location]]
        if dimension.lower() == 'latitude':
            profile_location = profile_location[::-1]
        self._datamap_profile.set_data(*profile_location)
        self._topomap_profile.set_data(*profile_location)

        self.ax_data.set_xlim(xlim)
        self.ax_topo.set_xlim(xlim)
        self.ax_topo.set_xlabel(dimension.capitalize())

        st.pyplot(self.fig)

    def interact(self):
        dim = self.default_dimension
        dim2 = set(self.data.dims).difference({dim}).pop()
        options = self.data[dim2].values.tolist()[::self.profile_interval]
        mid = options[len(options) // 2]

        dimension = st.sidebar.selectbox("Профиль вдоль", list(self.data.dims.keys()), index=0)
        location = st.sidebar.select_slider(f"на значении {dim2}", options=options, value=mid)

        self.plot(location, dimension)

def nc_app():
    st.title("Локальное гравитационное поле на основе данных гравитационной модели EIGEN-6c4, Глобальная ЦМР ETOPO1")
    
    st.write("""
    <div style="text-align: justify; margin-bottom: 20px;">
    Исходные данные о гравитации и топографии генерируются из моделей сферических гармоник с использованием [ICGEM Calculation Service](http://icgem.gfz-potsdam.de). 
    Данные распространяются в текстовых файлах, а высоты определяются относительно геоида (ортометрические высоты). 
    Необходимо преобразовать наблюдаемые высоты и топографию в геометрические высоты (относительно эллипсоида), используя высоты геоида, также загруженные из ICGEM. 
    Эти данные будут сохранены в файлах формата [netCDF](https://www.unidata.ucar.edu/software/netcdf/) для удобной загрузки с помощью [xarray](http://xarray.pydata.org/).
    </div>
    """, unsafe_allow_html=True)
    
    plot_hawaii_data(data, 'h_over_ellipsoid', cmap=cmocean.cm.delta)
    
    st.sidebar.title("Насыщенность цветовой шкалы")
    cutoff = st.sidebar.slider("Абсолютное значение отсечки (mGal)", min_value=50, max_value=600, step=50, value=150)
    
    crop_colorbar(cutoff)
    
    profile_selector = ProfileSelector(data, ['gravity_disturbance', 'gravity_bouguer'], figsize=(14, 6.8), projection=ccrs.PlateCarree())
    profile_selector.interact()
