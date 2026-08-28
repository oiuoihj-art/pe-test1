import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Физкультура", page_icon="🏃", layout="wide")

st.title("🏃 Система мониторинга физической подготовки")

# === Простые данные ===
@st.cache_data
def get_data():
    np.random.seed(42)
    data = []
    names = ["Иванов А.", "Петров Б.", "Сидоров В.", "Смирнова Г.", "Кузнецова Д."]
    
    for i, name in enumerate(names, 1):
        data.append({
            'ID': i,
            'Имя': name,
            '100м': round(12 + np.random.random(), 2),
            'Подтягивания': int(5 + np.random.random() * 10),
            'Прыжок (см)': int(180 + np.random.random() * 40)
        })
    return pd.DataFrame(data)

df = get_data()

# === Боковое меню ===
st.sidebar.title("Навигация")
page = st.sidebar.radio("Раздел:", ["Статистика", "Ученики", "Отстающие"])

# === Раздел 1 ===
if page == "Статистика":
    st.header("📊 Общая статистика")
    st.metric("Всего учеников", len(df))
    st.metric("Средний результат 100м", f"{df['100м'].mean():.2f} сек")
    st.metric("Среднее подтягивания", f"{df['Подтягивания'].mean():.1f} раз")
    
    st.subheader("Таблица результатов")
    st.dataframe(df)

# === Раздел 2 ===
elif page == "Ученики":
    st.header("👤 Анализ ученика")
    student = st.selectbox("Выберите ученика", df['Имя'])
    row = df[df['Имя'] == student].iloc[0]
    
    st.write(f"**{student}**")
    st.write(f"100м: {row['100м']} сек")
    st.write(f"Подтягивания: {row['Подтягивания']} раз")
    st.write(f"Прыжок: {row['Прыжок (см)']} см")

# === Раздел 3 ===
else:
    st.header("⚠️ Отстающие ученики")
    weak = df[df['Подтягивания'] < 10]
    st.write(f"Найдено {len(weak)} учеников")
    st.dataframe(weak)
