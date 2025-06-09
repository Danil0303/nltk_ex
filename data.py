import pandas as pd
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Определение приоритетов
PRIORITY_MAP = {
    "важно": 5,
    "очень важно": 4,
    "средне": 3,
    "не очень": 2,
    "пусто": 1,  # "пусто" - самый низкий приоритет
}


class DataFrameUpdater:
    """
    Класс для сравнения и обновления DataFrame на основе приоритетов.
    """

    def __init__(self, ip_col: str, computer_name_col: str, value_col: str, priority_map: dict = PRIORITY_MAP):
        """
        Инициализирует объект DataFrameUpdater.

        Args:
            ip_col (str): Название столбца с IP-адресами.
            computer_name_col (str): Название столбца с именами компьютеров.
            value_col (str): Название столбца со значениями "ценность".
            priority_map (dict, optional): Словарь, определяющий приоритеты значений. Defaults to PRIORITY_MAP.
        """
        self.ip_col = ip_col
        self.computer_name_col = computer_name_col
        self.value_col = value_col
        self.priority_map = priority_map

    def compare_and_update_dataframe(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """
        Сравнивает два DataFrame по IP-адресу и имени компьютера.
        Если приоритет "ценности" в df2 выше, то заменяет значения в df1
        соответствующими значениями из df2 (только для тех столбцов, которые есть в df2).
        df1 - изменяемый DataFrame, df2 - источник данных.

        Args:
            df1 (pd.DataFrame): Изменяемый DataFrame.
            df2 (pd.DataFrame): DataFrame с данными для сравнения.

        Returns:
            pd.DataFrame: Измененный df1.
        """

        # 1. Проверка на наличие необходимых столбцов
        if not all(col in df1.columns and col in df2.columns for col in [self.ip_col, self.computer_name_col, self.value_col]):
            logging.error(f"Отсутствуют необходимые столбцы в DataFrame: {self.ip_col}, {self.computer_name_col}, {self.value_col}")
            return df1  # Возвращаем исходный DataFrame

        # 2. Создание столбца с приоритетами в df1 и df2
        def get_priority(value):
            """Возвращает приоритет значения, используя словарь priority_map."""
            value = str(value).lower()  # Преобразуем в нижний регистр для сравнения
            return self.priority_map.get(value, 0)  # Если значение не найдено, присваиваем минимальный приоритет

        df1['priority'] = df1[self.value_col].apply(get_priority)
        df2['priority'] = df2[self.value_col].apply(get_priority)

        # 3. Объединение df1 и df2 для сравнения
        merged = pd.merge(
            df1,
            df2,
            on=[self.ip_col, self.computer_name_col],
            how='left',  # Left join - сохраняем все строки из df1
            suffixes=('', '_df2'),  # Добавляем суффикс для различия столбцов
            indicator=True,
        )

        # 4. Обновление значений в df1 на основе приоритета из df2 (если есть)
        def update_row(row):
            if row['_merge'] == 'both':  # Строка присутствует в обоих DataFrame
                if row['priority'] < row['priority_df2']:
                    # Заменяем значения из df2 для всех столбцов, которые есть в df2
                    for col in df2.columns:
                        if col not in [self.ip_col, self.computer_name_col, 'priority']:  # Пропускаем ключевые столбцы
                            row[col] = row[f'{col}_df2']  # Берем значения из df2
            return row

        df1_updated = merged.apply(update_row, axis=1)

        # 5. Возвращаем только столбцы df1 (все столбцы) и удаляем вспомогательные столбцы
        df1_updated = df1_updated.drop(columns=['priority', 'priority_df2', '_merge'], errors='ignore')

        # 6.  Сохраняем столбцы из df1 в том же порядке
        existing_cols = [col for col in df1.columns if col in df1_updated.columns] #Сохраняем столбцы, которые есть в обоих DataFrame
        df1_updated = df1_updated[existing_cols]

        logging.info("DataFrame успешно обработан.")
        return df1_updated


# ----------------------- Пример использования -----------------------
if __name__ == '__main__':
    # Создаем пример DataFrame df1 (изменяемый)
    data1 = {
        'ip': ['192.168.1.10', '192.168.1.10', '192.168.1.20', '192.168.1.30'],
        'computer_name': ['PC-1', 'PC-1', 'PC-2', 'PC-3'],
        'ценность': ['пусто', 'важно', 'средне', 'не очень'],
        'other_col1': ['data1', 'data2', 'data3', 'data4'],  # Добавлено больше столбцов
        'other_col2': [10, 20, 30, 40],
        'other_col3': [1.1, 2.2, 3.3, 4.4]
    }
    df1 = pd.DataFrame(data1)

    # Создаем пример DataFrame df2 (источник данных)
    data2 = {
        'ip': ['192.168.1.10', '192.168.1.20'],
        'computer_name': ['PC-1', 'PC-2'],
        'ценность': ['пусто', 'очень важно'],
        'other_col1': ['dataA', 'dataB'],  # Добавлены данные для проверки сохранения других столбцов
        'other_col2': [400, 200],
        'other_col3': [10.5, 20.2]
    }
    df2 = pd.DataFrame(data2)

    # Создаем экземпляр класса DataFrameUpdater
    updater = DataFrameUpdater(ip_col='ip', computer_name_col='computer_name', value_col='ценность')

    # Вызываем функцию для сравнения и обновления df1
    updated_df1 = updater.compare_and_update_dataframe(
        df1.copy(),
        df2,
    )

    # Выводим результат
    print("Исходный DataFrame df1:")
    print(df1)
    print("\nИсходный DataFrame df2:")
    print(df2)
    print("\nОбработанный DataFrame df1 (после обновления):")
    print(updated_df1)