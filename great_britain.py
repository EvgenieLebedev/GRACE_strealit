import streamlit as st

def great_britain_app():

    image_path = './landgrav_csv/GreatBritain.png'

    st.title("Анализ данных гравитационного исследования")
    st.write("""
    В разделе отображены данные из стандартного формата BGS (Британская Геологическая Служба) для наземных гравитационных исследований. Ниже приведены ключевые поля в наборе данных:

    - **SURVEY_AREA**: Область исследования
    - **STATION_ID**: Идентификатор станции
    - **STATION_CODE**: Код станции
    - **LATITUDE**: Широта (OSGB36, положительные значения к северу)
    - **LONGITUDE**: Долгота (OSGB36, положительные значения к востоку)
    - **STATION_ELEV**: Высота (станции), метры
    - **BOUGUER_DENS**: Плотность редукции Буге, Mg m-3
    - **OBSERVED_GRAV**: Наблюдаемый потенциал силы тяжести, mGal
    - **FREE AIR AN**: Аномалия свободного воздуха, mGal
    - **TOT_TC**: Полная коррекция рельефа, mGal
    - **BOUGUER ANOMALY**: Аномалия Буге, mGal

   """)

    st.image(image_path, caption='Карта гравитационных аномалий Великобритании')

    st.markdown("""
    <div style="text-align: justify;">
    Аномалии были рассчитаны с учетом геодезической справочной системы 1967 года (GRS67), Международной сети стандартизации гравитации 1971 года (IGSN71) и Национальной гравитационной справочной сети 1973 года (NGRN73).
    </div>
    """, unsafe_allow_html=True)