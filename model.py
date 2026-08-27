"""
Обучение модели классификации профессиональной ориентации.
Используется ML Pipeline (ColumnTransformer + Pipeline).
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# === 1. Категории профессий ===
CAREER_CATEGORIES = [
    "Технологии и IT",
    "Гуманитарные науки",
    "Естественные науки",
    "Искусство и дизайн",
    "Бизнес и экономика",
    "Медицина и здоровье"
]

# === 2. Генерация синтетического датасета ===
def generate_dataset(n_samples=2000, seed=42):
    np.random.seed(seed)
    
    # Оценки по предметам (1-10)
    math      = np.random.randint(1, 11, n_samples)
    russian   = np.random.randint(1, 11, n_samples)
    physics   = np.random.randint(1, 11, n_samples)
    chemistry = np.random.randint(1, 11, n_samples)
    biology   = np.random.randint(1, 11, n_samples)
    history   = np.random.randint(1, 11, n_samples)
    literature= np.random.randint(1, 11, n_samples)
    it        = np.random.randint(1, 11, n_samples)
    english   = np.random.randint(1, 11, n_samples)
    
    # Интересы (шкала 1-10)
    people    = np.random.randint(1, 11, n_samples)
    data      = np.random.randint(1, 11, n_samples)
    creativity= np.random.randint(1, 11, n_samples)
    tech      = np.random.randint(1, 11, n_samples)
    nature    = np.random.randint(1, 11, n_samples)
    business  = np.random.randint(1, 11, n_samples)
    
    # Формируем целевую переменную по "весам"
    scores = np.stack([
        math + it + tech + data*0.7,                # IT
        russian + literature + history + people*0.8,# Гуманитарные
        physics + chemistry + biology + nature*0.9, # Естественные
        creativity + literature + art_like(creativity),# Искусство
        business + math + english + people*0.6,     # Бизнес
        biology + chemistry + people + nature       # Медицина
    ], axis=1)
    
    target = np.argmax(scores, axis=1)
    
    df = pd.DataFrame({
        "math": math, "russian": russian, "physics": physics,
        "chemistry": chemistry, "biology": biology, "history": history,
        "literature": literature, "it": it, "english": english,
        "people": people, "data": data, "creativity": creativity,
        "tech": tech, "nature": nature, "business": business,
        "career": target
    })
    return df

def art_like(c):
    # небольшой шум для класса "Искусство"
    return np.random.normal(0, 1, size=c.shape)

# === 3. Построение ML Pipeline ===
def build_pipeline():
    numeric_features = [
        "math", "russian", "physics", "chemistry", "biology",
        "history", "literature", "it", "english",
        "people", "data", "creativity", "tech", "nature", "business"
    ]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight="balanced"
        ))
    ])
    return pipeline, numeric_features

# === 4. Обучение и сохранение ===
def train_and_save(model_path="career_model.pkl", encoder_path="career_map.pkl"):
    df = generate_dataset()
    X = df.drop("career", axis=1)
    y = df["career"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    pipeline, _ = build_pipeline()
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    print(f"✅ Точность модели: {accuracy_score(y_test, y_pred):.4f}")
    print("\n" + classification_report(y_test, y_pred, target_names=CAREER_CATEGORIES))
    
    joblib.dump(pipeline, model_path)
    joblib.dump(CAREER_CATEGORIES, encoder_path)
    print(f"💾 Модель сохранена: {model_path}")
    return pipeline

if __name__ == "__main__":
    train_and_save()
