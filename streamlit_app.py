import streamlit as st
from st import extract_dates_from_filenames
from gravity import talwani
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
import os

def main():
    st.title("ВКР Лебедев Е.Д. ПИабпд-1м")

    app_mode = st.sidebar.selectbox("Выберите приложение", ["Визуализация данных GRACE", "Расчет гравитационного потенциала 2D (Talwani)"])

    if app_mode == "Визуализация данных GRACE":
        grace_app()
    elif app_mode == "Расчет гравитационного потенциала 2D (Talwani)":
        gravity_app()

def grace_app():
    images_dir = "GRACE"
    dates = extract_dates_from_filenames(images_dir)

    st.write("Этот проект выполнен Лебедевым Е.Д. в рамках магистерской ВКР по исследованию поля силы тяжести")

    selected_date = st.selectbox('Выберите дату', dates)

    selected_image = f"GRACE_{selected_date}.png"
    image_path = os.path.join(images_dir, selected_image)

    if os.path.exists(image_path):
        st.image(image_path, caption=f"Данные GRACE за {selected_date}", use_column_width=True)
    else:
        st.write("Изображение не найдено.")

def gravity_app():
    st.write("""
    <div style="text-align: justify; margin-bottom: 20px;">
    Маник Талвани разработал метод расчет гравитационной аномалии, обусловленной многоугольным телом в вертикальном поперечном сечении.
    При расчете модели используется контурный интеграл. 
    Гравитационная аномалия определяется путем вычисления линейного интеграла вдоль каждого ребра многоугольника (тела). 
    Результирующая гравитационная аномалия прямо пропорциональна сумме линейных интегралов и разнице плотности между телом и окружающей породой.
             
    </div>
    """, unsafe_allow_html=True)



    density_contrast_default = 500.0
    x_zero = 50
    x_scale = 100  
    depth_zero = 200  
    depth_scale = 100  
    mgal_zero = 190  
    mgal_scale = 10

    default_x = [100, 200, 200, 100]
    default_y = [120, 120, 20, 20]

    fig, ax = plt.subplots()

    density_contrast = st.slider('Плотность тела (кг/м2)', 1, 1000, int(density_contrast_default))

    col1, col2, col3, col4 = st.columns(4)

    x = []
    y = []
    for i in range(4):
        with col1 if i < 2 else col2:
            x.append(st.number_input(f'Point {i+1} X', min_value=0, max_value=600, value=default_x[i]))
        with col3 if i < 2 else col4:
            y.append(st.number_input(f'Point {i+1} Y', min_value=0, max_value=200, value=default_y[i]))

    polygon = Polygon(np.column_stack((x, y)), closed=True, fill=None, edgecolor='r')
    ax.add_patch(polygon)
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 480)
    ax.axhline(y=depth_zero, color='k')
    ax.axvline(x=x_zero, color='k')
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Depth (km)')
    ax.set_title('2D Polygon')

    gravity_values = []
    step_size = min(25, int((max(x) - x_zero) / 10))  
    for offset in range(x_zero, 600, step_size):
        gravity = 0
        for i in range(4):
            i2 = (i + 1) % 4
            x1m = (x[i] - offset) / x_scale * 1000
            x2m = (x[i2] - offset) / x_scale * 1000
            z1m = (y[i] - depth_zero) / depth_scale * 1000
            z2m = (y[i2] - depth_zero) / depth_scale * 1000
            gravity += talwani(x1m, x2m, z1m, z2m, density_contrast)
        del_grav = gravity * mgal_scale
        m = mgal_zero - del_grav
        gravity_values.append((offset, m))

    gravity_x, gravity_y = zip(*gravity_values)
    ax.plot(gravity_x, gravity_y, 'ro')
    ax.axhline(y=mgal_zero, color='k')
    ax.axvline(x=x_zero, color='k')
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Gravity (mGal)')
    ax.set_title('Gravity Anomaly')

    st.pyplot(fig)

    st.write("""
    ### Инструкции
    - Установите требуемую плотность тела
    - Введите координаты 4 точек, чтобы определить полигон. 
    - Точки должны располагаться в порядке обхода по часовой стрелке !
    """)

if __name__ == "__main__":
    main()
