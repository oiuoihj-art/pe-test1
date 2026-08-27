import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Физкультура — Аналитика", page_icon="🏃", layout="wide")

st.title("🏃 Система мониторинга физической подготовки учащихся")
st.markdown("**Аналитический дашборд для учителя физкультуры**")

# === Генерация данных ===
@st.cache_data
def generate_data():
    np.random.seed(42)
    students = []
    student_id = 1
    
    for test_num in range(1, 6):
        for _ in range(30):
            base_fitness = np.random.normal(0, 1)
            progress = 1 + (test_num - 1) * 0.02
            
            students.append({
                'student_id': student_id,
                'test_number': test_num,
                'run_100m': (11.5 - base_fitness * 0.8 + np.random.normal(0, 0.5)) / progress,
                'pull_ups': (8 + base_fitness * 4 + np.random.normal(0, 2)) * progress,
                'long_jump': (200 + base_fitness * 20 + np.random.normal(0, 10)) * progress,
                'shuttle_run': (25 - base_fitness * 2 + np.random.normal(0, 1)) / progress,
                'abs_exercises': (40 + base_fitness * 10 + np.random.normal(0, 5)) * progress
            })
            student_id += 1
    
    return pd.DataFrame(students)

df = generate_data()

# === Боковая панель ===
st.sidebar.header("📊 Навигация")
page = st.sidebar.radio("Выберите раздел", [
    "📈 Общая статистика",
    "👤 Анализ ученика",
    "⚠️ Отстающие ученики"
])

# === Страница 1: Общая статистика ===
if page == "📈 Общая статистика":
    st.header("📈 Общая статистика класса")
    
    latest = df[df['test_number'] == 5]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Учеников", f"{latest['student_id'].nunique()}")
    with col2:
        st.metric("Среднее 100м", f"{latest['run_100m'].mean():.2f} сек")
    with col3:
        st.metric("Подтягивания", f"{latest['pull_ups'].mean():.1f} раз")
    with col4:
        st.metric("Прыжок в длину", f"{latest['long_jump'].mean():.1f} см")
    
    st.markdown("---")
    st.subheader("📊 Динамика результатов класса")
    
    progress = df.groupby('test_number').mean().reset_index()
    
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=('100м бег', 'Подтягивания', 'Прыжок в длину',
                                       'Челночный бег', 'Пресс'))
    
    metrics = [
        ('run_100m', 1, 1, 'red'),
        ('pull_ups', 1, 2, 'blue'),
        ('long_jump', 1, 3, 'green'),
        ('shuttle_run', 2, 1, 'orange'),
        ('abs_exercises', 2, 2, 'purple')
    ]
    
    for col, row, col_num, color in metrics:
        fig.add_trace(
            go.Scatter(x=progress['test_number'], y=progress[col],
                      mode='lines+markers', name=col, line=dict(color=color)),
            row=row, col=col_num
        )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# === Страница 2: Анализ ученика ===
elif page == "👤 Анализ ученика":
    st.header("👤 Анализ конкретного ученика")
    
    student_id = st.selectbox("Выберите ученика", 
                              sorted(df['student_id'].unique()),
                              format_func=lambda x: f"Ученик #{x}")
    
    student_data = df[df['student_id'] == student_id].sort_values('test_number')
    
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=('100м бег', 'Подтягивания', 'Прыжок в длину',
                                       'Челночный бег', 'Пресс'))
    
    metrics = [
        ('run_100m', 1, 1, 'red'),
        ('pull_ups', 1, 2, 'blue'),
        ('long_jump', 1, 3, 'green'),
        ('shuttle_run', 2, 1, 'orange'),
        ('abs_exercises', 2, 2, 'purple')
    ]
    
    for col, row, col_num, color in metrics:
        fig.add_trace(
            go.Scatter(x=student_data['test_number'], y=student_data[col],
                      mode='lines+markers', name=col, line=dict(color=color)),
            row=row, col=col_num
        )
    
    fig.update_layout(height=500, showlegend=False, title_text=f"Динамика ученика #{student_id}")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Результаты тестов")
    st.dataframe(student_data.round(2), use_container_width=True)

# === Страница 3: Отстающие ученики ===
elif page == "⚠️ Отстающие ученики":
    st.header("⚠️ Отстающие ученики")
    
    latest = df[df['test_number'] == 5].copy()
    latest['run_100m_score'] = -latest['run_100m']
    latest['shuttle_run_score'] = -latest['shuttle_run']
    
    score_cols = ['run_100m_score', 'pull_ups', 'long_jump', 'shuttle_run_score', 'abs_exercises']
    latest['total_score'] = latest[score_cols].sum(axis=1)
    
    threshold = latest['total_score'].quantile(0.25)
    at_risk = latest[latest['total_score'] <= threshold]
    
    st.warning(f"Выявлено **{len(at_risk)}** учеников с результатами ниже 25-го перцентиля")
    
    if len(at_risk) > 0:
        st.dataframe(at_risk[['student_id', 'run_100m', 'pull_ups', 'long_jump', 
                              'shuttle_run', 'abs_exercises']].round(2), use_container_width=True)
        
        st.subheader("💡 Рекомендации")
        st.markdown("""
        1. **Индивидуальный подход** — разработать персональные программы
        2. **Дополнительные занятия** — организовать факультативные тренировки
        3. **Мотивация** — поставить конкретные достижимые цели
        4. **Мониторинг** — отслеживать прогресс еженедельно
        """)
    else:
        st.success("Все ученики показывают удовлетворительные результаты!")
