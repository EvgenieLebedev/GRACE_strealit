import streamlit as st
import matplotlib.pyplot as plt
import os

def extract_dates_from_filenames(directory):
    filenames = os.listdir(directory)
    dates = []
    for filename in filenames:
        parts = filename.split("_")
        if len(parts) == 4 and parts[0] == "GRACE":
            date_string = "_".join(parts[1:]).split(".")[0]  # Убираем расширение файла
            dates.append(date_string)
    dates.sort()  # Сортируем даты по возрастанию
    return dates
