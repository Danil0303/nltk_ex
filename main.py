import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import joblib  # Для сохранения и загрузки модели
import os # для работы с файловой системой


# -------------------  Данные  -------------------

# Классы и их примеры (расширенные)
class_samples = {
    'положительно': [
        'Отличное качество!', 'Очень доволен покупкой', 'Превосходный сервис',
        'Рекомендую всем!', 'Превзошло ожидания', 'Идеально!', 'Все супер!',
        'Отлично!', 'Рад покупке', 'Буду советовать'
    ],
    'негативно': [
        'Ужасное качество', 'Очень разочарован', 'Отвратительный сервис',
        'Никому не рекомендую', 'Не оправдало ожиданий', 'Полное разочарование',
        'Ужасно!', 'Плохо!', 'Не доволен', 'Не стоит своих денег'
    ],
    'нейтрально': [
        'Нормально', 'Неплохо', 'Средне', 'Обычный продукт', 'Ничего особенного',
        'Сойдет', 'Без восторгов', 'Не плохо, не хорошо', 'Как обычно', 'Стандартно'
    ],
    'жалоба': [
        'Брак товара', 'Повреждено при доставке', 'Не работает', 'Не хватает деталей',
        'Проблема с оплатой', 'Долго ждал доставку', 'Неправильный размер',
        'Неверная комплектация', 'Не получил заказ', 'Товар не соответствует описанию'
    ],
    'вопрос': [
        'Как использовать?', 'Когда будет доставка?', 'Сколько стоит?', 'Есть ли гарантия?',
        'Как вернуть товар?', 'Где найти инструкцию?', 'Какой срок годности?',
        'Можно ли оплатить картой?', 'Есть ли в наличии?', 'Как связаться с вами?'
    ],
    'предложение': [
        'Сделайте скидку!', 'Добавьте этот товар!', 'Улучшите сервис!',
        'Расширьте ассортимент', 'Пожалуйста, перезвоните!', 'Хочу больше акций!',
        'Предлагаю сотрудничество', 'Сделайте бесплатную доставку', 'Добавьте этот цвет', 'Улучшите упаковку'
    ],
    'благодарность': [
        'Спасибо за быструю доставку!', 'Спасибо за помощь', 'Очень благодарен',
        'Спасибо за отличную работу!', 'Спасибо за подарок', 'Вы лучшие!',
        'Спасибо!', 'Благодарю!', 'Спасибо, что помогли', 'Спасибо за понимание'
    ]
}


# Расширим данные до 1000 примеров, балансируя классы
def generate_data(class_samples, total_samples=1000):
    texts = []
    labels = []
    num_classes = len(class_samples)
    samples_per_class = total_samples // num_classes #постараемся создать одинаковое кол-во примеров
    remainder = total_samples % num_classes
    class_names = list(class_samples.keys())

    for i in range(num_classes):
        class_name = class_names[i]
        num_samples = samples_per_class + (1 if i < remainder else 0)  # Распределение остатка
        for _ in range(num_samples):
            text = random.choice(class_samples[class_name])
            texts.append(text)
            labels.append(class_name)
    random.shuffle(texts) # Перемешиваем данные
    random.shuffle(labels)
    return texts, labels



texts, labels = generate_data(class_samples, total_samples=1000)

# Создаём DataFrame
df = pd.DataFrame({'text': texts, 'label': labels})

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

# Векторизация текста
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Обучение модели
model = MultinomialNB()
model.fit(X_train_vec, y_train)


# Предсказания и оценка
y_pred = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))


# Функция для тестирования модели
def evaluate_model(model, vectorizer, texts):
    """
    Обрабатывает список текстов и возвращает предсказанные метки.

    Parameters:
    - model: обученная модель
    - vectorizer: векторизатор, использованный при обучении
    - texts: список или серия текстовых данных

    Returns:
    - предсказания модели
    """
    texts_vec = vectorizer.transform(texts)
    predictions = model.predict(texts_vec)
    return predictions


# Функция для сохранения модели и векторизатора в один файл
def save_model_to_file(model, vectorizer, filename='sentiment_model.joblib'):
    """
    Сохраняет модель и векторизатор в один файл.
    Использует словарь для сохранения обоих объектов.

    Parameters:
    - model: обученная модель
    - vectorizer: векторизатор, использованный при обучении
    - filename: имя файла для сохранения
    """
    objects_to_save = {
        'model': model,
        'vectorizer': vectorizer
    }
    joblib.dump(objects_to_save, filename)
    print(f"Модель и векторизатор сохранены в файл: {filename}")


# Функция для загрузки модели и векторизатора из одного файла
def load_model_from_file(filename='sentiment_model.joblib'):
    """
    Загружает модель и векторизатор из одного файла.

    Returns:
    - model: загруженная модель
    - vectorizer: загруженный векторизатор
    """
    try:
        loaded_objects = joblib.load(filename)
        model = loaded_objects['model']
        vectorizer = loaded_objects['vectorizer']
        print(f"Модель и векторизатор загружены из файла: {filename}")
        return model, vectorizer
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return None, None # или выбросить исключение, если это критично


# Пример использования функции
new_texts = [
    'Отличное качество!',
    'Ужасное обслуживание',
    'Нормально, как всегда',
    'Брак товара, что делать?',
    'Когда будет доставка?',
    'Сделайте скидку!',
    'Спасибо за помощь!'
]


if __name__ == '__main__':
    # Сохраняем модель и векторизатор в один файл
    save_model_to_file(model, vectorizer)

    # Загружаем модель и векторизатор из одного файла
    loaded_model, loaded_vectorizer = load_model_from_file()

    if loaded_model and loaded_vectorizer:
        # Проверяем работу загруженной модели
        predictions = evaluate_model(loaded_model, loaded_vectorizer, new_texts)
        for text, pred in zip(new_texts, predictions):
            print(f"Текст: '{text}' - Предсказание: {pred}")
    else:
        print("Не удалось загрузить модель и векторизатор.")
