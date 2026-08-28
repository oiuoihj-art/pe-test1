import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Физкультура — Аналитика", page_icon="🏃", layout="wide")

st.title("🏃 Система мониторинга физической подготовки учащихся")
st.markdown("**Аналитический дашборд для учителя физкультуры**")

# === Список имён ===
FIRST_NAMES = [
    "Александр", "Дмитрий", "Максим", "Сергей", "Андрей",
    "Алексей", "Артём", "Илья", "Кирилл", "Михаил",
    "Анна", "Мария", "Дарья", "Анастасия", "Екатерина",
    "Полина", "Виктория", "София", "Алиса", "Валерия"
]

LAST_NAMES_M = ["Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев",
                "Петров", "Соколов", "Михайлов", "Новиков", "Фёдоров"]

LAST_NAMES_F = ["Иванова", "Смирнова", "Кузнецова", "Попова", "Васильева",
                "Петрова", "Соколова", "Михайлова", "Новикова", "Фёдорова"]

# === Генерация данных ===
@st.cache_data
def generate_data():
    np.random.seed(42)
    students = []
    
    student_names = {}
    for i in range(1, 31):
        first_name = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        if i % 2 == 0:
            last_name = LAST_NAMES_F[(i - 1) % len(LAST_NAMES_F)]
        else:
            last_name = LAST_NAMES_M[(i - 1) % len(LAST_NAMES_M)]
        student_names[i] = f"{last_name} {first_name}"
    
    for test_num in range(1, 6):
        for i in range(1, 31):
            base_fitness = np.random.normal(0, 1)
            progress = 1 + (test_num - 1) * 0.02
            
            students.append({
                'student_id': i,
                'student_name': student_names[i],
                'test_number': test_num,
                'run_100m': round((11.5 - base_fitness * 0.8 + np.random.normal(0, 0.5)) / progress, 2),
                'pull_ups': max(0, int((8 + base_fitness * 4 + np.random.normal(0, 2)) * progress)),
                'long_jump': int((200 + base_fitness * 20 + np.random.normal(0, 10)) * progress),
                'shuttle_run': round((25 - base_fitness * 2 + np.random.normal(0, 1)) / progress, 2),
                'abs_exercises': max(0, int((40 + base_fitness * 10 + np.random.normal(0, 5)) * progress))
            })
    
    return pd.DataFrame(students)

df = generate_data()

# === Боковая панель ===
st.sidebar.header("📊 Навигация")

# Используем индексы вместо текста
page_index = st.sidebar.radio("Выберите раздел", [0, 1, 2], 
                               format_func=lambda x: ["📈 Общая статистика", 
                                                     "👤 Анализ ученика", 
                                                     "⚠️ Отстающие ученики"][x])

# === Страница 1: Общая статистика ===
if page_index == 0:
    st.header(" Общая статистика класса")
    
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
    
    # График 1: Динамика класса
    st.subheader("📊 Динамика результатов класса по тестам")
    
    progress = df.groupby('test_number').agg({
        'run_100m': 'mean',
        'pull_ups': 'mean',
        'long_jump': 'mean',
        'shuttle_run': 'mean',
        'abs_exercises': 'mean'
    }).reset_index()
    
    fig_progress = make_subplots(rows=2, cols=3,
                                  subplot_titles=('100м бег (сек)', 'Подтягивания (раз)', 'Прыжок в длину (см)',
                                                 'Челночный бег (сек)', 'Пресс (раз)'))
    
    metrics = [
        ('run_100m', 1, 1, '#FF6B6B'),
        ('pull_ups', 1, 2, '#4ECDC4'),
        ('long_jump', 1, 3, '#45B7D1'),
        ('shuttle_run', 2, 1, '#FFA07A'),
        ('abs_exercises', 2, 2, '#98D8C8')
    ]
    
    for col, row, col_num, color in metrics:
        fig_progress.add_trace(
            go.Scatter(x=progress['test_number'], y=progress[col],
                      mode='lines+markers', name=col, line=dict(color=color, width=3),
                      marker=dict(size=8)),
            row=row, col=col_num
        )
    
    fig_progress.update_layout(height=600, showlegend=False, 
                               title_text="Прогресс класса от теста к тесту")
    fig_progress.update_xaxes(title_text="Номер теста")
    st.plotly_chart(fig_progress, use_container_width=True)
    
    # График 2: Распределение результатов
    st.subheader("📊 Распределение результатов (последний тест)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist1 = px.histogram(latest, x='pull_ups', nbins=10,
                                 title='Подтягивания: распределение',
                                 labels={'pull_ups': 'Количество раз'},
                                 color_discrete_sequence=['#4ECDC4'])
        fig_hist1.add_vline(x=latest['pull_ups'].mean(), line_dash="dash", 
                           line_color="red", annotation_text="Среднее")
        st.plotly_chart(fig_hist1, use_container_width=True)
    
    with col2:
        fig_hist2 = px.histogram(latest, x='long_jump', nbins=10,
                                 title='Прыжок в длину: распределение',
                                 labels={'long_jump': 'Сантиметры'},
                                 color_discrete_sequence=['#45B7D1'])
        fig_hist2.add_vline(x=latest['long_jump'].mean(), line_dash="dash", 
                           line_color="red", annotation_text="Среднее")
        st.plotly_chart(fig_hist2, use_container_width=True)
    
    # График 3: Топ учеников
    st.subheader("🏆 Топ-10 учеников по подтягиваниям")
    
    top_pullups = latest.nlargest(10, 'pull_ups')[['student_name', 'pull_ups']]
    
    fig_top = px.bar(top_pullups, x='student_name', y='pull_ups',
                     title='Лучшие результаты по подтягиваниям',
                     labels={'student_name': 'Ученик', 'pull_ups': 'Раз'},
                     color='pull_ups',
                     color_continuous_scale='Viridis')
    fig_top.update_layout(xaxis_tickangle=-45, height=400, showlegend=False)
    st.plotly_chart(fig_top, use_container_width=True)

# === Страница 2: Анализ ученика ===
elif page_index == 1:
    st.header("👤 Анализ конкретного ученика")
    
    # Получаем список учеников
    latest_names = df[df['test_number'] == 5][['student_id', 'student_name']].drop_duplicates()
    
    # Создаем словарь: ключ - отображаемое имя, значение - ID
    student_dict = {}
    for _, row in latest_names.iterrows():
        display_name = f"{row['student_name']} (ID: {row['student_id']})"
        student_dict[display_name] = row['student_id']
    
    # Выбор ученика
    selected_name = st.selectbox("Выберите ученика", list(student_dict.keys()))
    
    # Получаем ID из словаря (надёжно!)
    student_id = student_dict[selected_name]
    student_name = selected_name.split(" (ID:")[0]
    
    # Получаем данные
    student_data = df[df['student_id'] == student_id].sort_values('test_number')
    
    st.subheader(f" Динамика: {student_name}")
    
    # График
    fig = make_subplots(rows=2, cols=3,
                        subplot_titles=('100м бег (сек)', 'Подтягивания (раз)', 'Прыжок (см)',
                                       'Челночный бег (сек)', 'Пресс (раз)'))
    
    metrics = [
        ('run_100m', 1, 1, '#FF6B6B'),
        ('pull_ups', 1, 2, '#4ECDC4'),
        ('long_jump', 1, 3, '#45B7D1'),
        ('shuttle_run', 2, 1, '#FFA07A'),
        ('abs_exercises', 2, 2, '#98D8C8')
    ]
    
    for col, row, col_num, color in metrics:
        fig.add_trace(
            go.Scatter(x=student_data['test_number'], y=student_data[col],
                      mode='lines+markers', name=col, line=dict(color=color, width=3),
                      marker=dict(size=10)),
            row=row, col=col_num
        )
    
    fig.update_layout(height=500, showlegend=False, title_text="Индивидуальная динамика")
    fig.update_xaxes(title_text="Номер теста")
    st.plotly_chart(fig, use_container_width=True)
    
    # Таблица
    st.subheader("📋 Результаты по тестам")
    display_df = student_data[['test_number', 'run_100m', 'pull_ups', 'long_jump', 
                               'shuttle_run', 'abs_exercises']].copy()
    display_df.columns = ['Тест', '100м (сек)', 'Подтягивания', 'Прыжок (см)', 
                          'Челночный бег (сек)', 'Пресс (раз)']
    st.dataframe(display_df.round(2), use_container_width=True)

# === Страница 3: Отстающие ученики ===
else:  # page_index == 2
    st.header("⚠️ Отстающие ученики")
    
    latest = df[df['test_number'] == 5].copy()
    
    # Нормализуем
    latest['run_100m_score'] = -latest['run_100m']
    latest['shuttle_run_score'] = -latest['shuttle_run']
    
    # Считаем рейтинг
    score_cols = ['run_100m_score', 'pull_ups', 'long_jump', 'shuttle_run_score', 'abs_exercises']
    latest['total_score'] = latest[score_cols].sum(axis=1)
    
    # Порог
    threshold = latest['total_score'].quantile(0.25)
    at_risk = latest[latest['total_score'] <= threshold]
    
    st.warning(f"Выявлено **{len(at_risk)}** учеников с результатами ниже 25-го перцентиля")
    
    if len(at_risk) > 0:
        # Таблица
        display_df = at_risk[['student_name', 'run_100m', 'pull_ups', 'long_jump', 
                              'shuttle_run', 'abs_exercises']].copy()
        display_df.columns = ['Ученик', '100м (сек)', 'Подтягивания', 'Прыжок (см)', 
                              'Челночный бег (сек)', 'Пресс (раз)']
        st.dataframe(display_df.round(2), use_container_width=True)
        
        # График
        st.subheader("📊 Сравнение отстающих со средним по классу")
        
        class_avg = latest[['pull_ups', 'long_jump', 'abs_exercises']].mean()
        at_risk_avg = at_risk[['pull_ups', 'long_jump', 'abs_exercises']].mean()
        
        comparison_df = pd.DataFrame({
            'Показатель': ['Подтягивания', 'Прыжок (см)', 'Пресс (раз)'],
            'Класс (среднее)': [class_avg['pull_ups'], class_avg['long_jump'], class_avg['abs_exercises']],
            'Отстающие (среднее)': [at_risk_avg['pull_ups'], at_risk_avg['long_jump'], at_risk_avg['abs_exercises']]
        })
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name='Класс', x=comparison_df['Показатель'], 
                                  y=comparison_df['Класс (среднее)'],
                                  marker_color='#4ECDC4'))
        fig_comp.add_trace(go.Bar(name='Отстающие', x=comparison_df['Показатель'],
                                  y=comparison_df['Отстающие (среднее)'],
                                  marker_color='#FF6B6B'))
        
        fig_comp.update_layout(barmode='group', height=400, 
                               title="Сравнение средних показателей")
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Рекомендации
        st.subheader("💡 Рекомендации")
        st.markdown("""
        1. **Индивидуальный подход** — разработать персональные программы тренировок
        2. **Дополнительные занятия** — организовать факультативные тренировки 2-3 раза в неделю
        3. **Мотивация** — поставить конкретные достижимые цели на месяц
        4. **Мониторинг** — отслеживать прогресс еженедельно
        5. **Работа с родителями** — информировать о результатах и рекомендациях
        """)
    else:
        st.success("✅ Все ученики показывают удовлетворительные результаты!")
