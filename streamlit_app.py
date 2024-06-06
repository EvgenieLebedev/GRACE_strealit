import streamlit as st
from st import extract_dates_from_filenames
from gravity import talwani
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
import os
from nc_calculate import nc_app  # Импорт функции nc_app из nc_calculate

def main():
    st.title("ВКР Лебедев Е.Д. ПИабпд-1м")

    app_mode = st.sidebar.selectbox("Выберите приложение", [
        "Визуализация данных GRACE", 
        "Редукция бурге",
        "Расчет гравитационного потенциала 2D (Talwani)" 
        
    ])

    if app_mode == "Визуализация данных GRACE":
        grace_app()
    elif app_mode == "Расчет гравитационного потенциала 2D (Talwani)":
        gravity_app()
    elif app_mode == "Редукция бурге":
        nc_app()

def grace_app():
    images_dir = "GRACE"
    dates = extract_dates_from_filenames(images_dir)

    st.write("""
    <div style="text-align: justify; margin-bottom: 20px;">
    Зонд GRACE измеряет силу земного притяжения исключительно простым способом. 
    Во время полета расстояние между двумя аппаратами непрерывно отслеживается с очень высокой точностью. 
    Если бы Земля была однородным шаром, то сила тяжести была бы одинаковой во всех точках круговой орбиты. 
    Спутники бы тогда двигались со строго постоянной скоростью, и расстояние между ними всегда оставалось бы неизменным. 
    Однако на реальной Земле есть профиль — горы, долины, океаны, а также те неоднородности земной коры, которые скрываются под поверхностью. 
    Они тоже оказывают гравитационное воздействие на спутники, а значит, и слегка влияют на их движение. 
    Это дополнительное гравитационное воздействие приводит, в частности, к небольшим изменениям расстояния между спутниками.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("""
    <div style="text-align: justify; margin-bottom: 20px;">
    Ниже приведены данные, полученные путем построения моделей на основе месячных данных с 2002 по 2024 года.
    
    [Источник данных](https://grace.jpl.nasa.gov/data/get-data/)
    </div>
    """, unsafe_allow_html=True)

    selected_date = st.selectbox('Выберите дату', dates)

    selected_image = f"GRACE_{selected_date}.png"
    image_path = os.path.join(images_dir, selected_image)

    if os.path.exists(image_path):
        st.image(image_path, caption=f"Данные GRACE за {selected_date}", use_column_width=True)
    else:
        st.write("Изображение не найдено.")
    
    st.write("""
    <div style="text-align: justify; margin-bottom: 20px;">
    Продукты уровня 2 миссий GRACE и GRACE-FO состоят из коэффициентов сферических гармоник гравитационного поля Земли. Файлы данных модели сферических гармоник (SHM) обычно представляют собой сжатые gzip ASCII-файлы с именами, формат которых следующий: PID-2_YYYYDOY-yyyydoy_ndays_center_flag_rrrr или PID-2_YYYYDOY-yyyydoy_mssn_center_flag_rrrr.

    - PID — строка идентификации продукта (для стандартных продуктов: GSM, GAD, GAC, GAA, GAB).

    - -2 обозначает, что данные относятся к продукту уровня 2 миссии GRACE.

    - YYYYDOY обозначает начальную дату (год и день года) диапазона измерений.

    - yyyydoy обозначает конечную дату (год и день года) диапазона измерений.

    - ndays — количество календарных дней, использованных для получения месячной оценки.

    - mssn — миссия: GRAC для GRACE и GRFO для GRACE Follow-On.

    - center — строка, специфичная для учреждения (UTCSR для CSR, JPLEM для JPL Spherical Harmonics, JPLMSC для JPL Mascons, EIGEN или GFZOP для GFZ).

    - flag — строка из 4 символов, зависящая от центра обработки данных (CSR обозначает максимальную степень и, возможно, максимальный порядок решений, JPL обозначает промежуточный выпуск данных, GFZ обозначает ограниченные или неограниченные решения). Для выпуска Release-6 и последующих этот флаг обозначает процессинг.

    - rrrr — строка из 4 символов, обозначающая выпуск, обычно представляющая собой 4-значное число (в наборах данных GFZ может обозначать промежуточные выпуски в 4-м символе).
    </div>
    """, unsafe_allow_html=True)

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
            x.append(st.number_input(f'Точка {i+1} X', min_value=0, max_value=600, value=default_x[i]))
        with col3 if i < 2 else col4:
            y.append(st.number_input(f'Точка {i+1} Y', min_value=0, max_value=200, value=default_y[i]))

    polygon = Polygon(np.column_stack((x, y)), closed=True, fill=None, edgecolor='r')
    ax.add_patch(polygon)
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 480)
    ax.axhline(y=depth_zero, color='k')
    ax.axvline(x=x_zero, color='k')
    ax.set_xlabel('Расстояние (км)')
    ax.set_ylabel('Глубина (км)')
    ax.set_title('2D Полигон')

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
    ax.set_title('Гравитационный потенциал')

    st.pyplot(fig)

    st.write("""
    ### Инструкции
    - Установите требуемую плотность тела
    - Введите координаты 4 точек, чтобы определить полигон. 
    - Точки должны располагаться в порядке обхода по часовой стрелке !
    """)

    st.write("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2>Листинг кода для вычиления гравитационного потенциала</h2>
    </div>
    """, unsafe_allow_html=True)

    st.write("""
    ```py
    def talwani(x1, x2, z1, z2, density):
        G = 6.67e-11
        pi = np.pi
        epsilon = 1e-6  
        if x1 == 0:
            x1 += epsilon
        if x2 == 0:
            x2 += epsilon
        if (x2 - x1) == 0:
            x2 = x1 - epsilon
        denom = z2 - z1
        if denom == 0:
            denom = epsilon
        alpha = (x2 - x1) / denom
        beta = (x1 * z2 - x2 * z1) / denom
        factor = beta / (1 + alpha * alpha)
        r1sq = (x1 * x1 + z1 * z1)
        r2sq = (x2 * x2 + z2 * z2)
        term1 = 0.5 * (np.log(r2sq) - np.log(r1sq))
        term2 = np.arctan2(z2, x2) - np.arctan2(z1, x1)
        zz = factor * (term1 - alpha * term2)
        grav = 2 * G * density * zz * 1e5
        return -grav       
    ```
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
