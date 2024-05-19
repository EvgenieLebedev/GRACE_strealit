import streamlit as st
import matplotlib.pyplot as plt
import os

def extract_dates_from_filenames(directory):
    filenames = os.listdir(directory)
    dates = []
    for filename in filenames:
        parts = filename.split("_")
        if len(parts) == 4 and parts[0] == "GRACE":
            date_string = "_".join(parts[1:]).split(".")[0]  
            dates.append(date_string)
    dates.sort()  
    return dates

images_dir = "GRACE"
dates = extract_dates_from_filenames(images_dir)

st.title("Визуализация данных GRACE")
st.write("Этот проект выполнен Лебедевым Е.Д. в рамках магистерской ВКР по исследованию поля силы тяжести")


selected_date = st.selectbox('Выберите дату', dates)

selected_image = f"GRACE_{selected_date}.png"
image_path = os.path.join(images_dir, selected_image)

if os.path.exists(image_path):
    st.image(image_path, caption=f"Данные GRACE за {selected_date}", use_column_width=True)
else:
    st.write("Изображение не найдено.")
