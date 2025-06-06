import pandas as pd
import xlsxwriter

def format_dataframe_to_excel(df, filename='output.xlsx'):
    """
    Записывает DataFrame в Excel файл, автоматически подбирает ширину и высоту ячеек,
    закрашивает строки в зависимости от значения в столбце 'ценность' или 'анализ',
    и добавляет границы ко всей таблице.

    Args:
        df (pd.DataFrame): DataFrame для записи в Excel.
        filename (str): Имя файла Excel для сохранения.
    """

    # Создаем Excel writer с использованием xlsxwriter в качестве движка
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    # Записываем DataFrame на лист Excel
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Получаем workbook и worksheet объекты
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Определяем форматы ячеек
    yellow_format = workbook.add_format({'bg_color': '#FFFF00', 'border': 1})  # Желтый + граница
    blue_format = workbook.add_format({'bg_color': '#ADD8E6', 'border': 1})  # Синий + граница
    default_format = workbook.add_format({'border': 1}) # Формат с границей по умолчанию

    # ----------------------- Автоматическая подгонка ширины столбцов -----------------------
    for col_num, value in enumerate(df.columns.values):
        column_len = max(df[value].astype(str).str.len().max(),  # Длина данных
                         len(value))  # Длина заголовка столбца
        column_len = min(column_len, 50) #Ограничение ширины столбца
        worksheet.set_column(col_num, col_num, column_len + 2)  # +2 для небольшого запаса

    # ----------------------- Автоматическая подгонка высоты строк -----------------------
    for row_num in range(len(df)):
        max_row_height = 0
        for col_num in range(len(df.columns)):
            cell_value = str(df.iloc[row_num, col_num])
            num_lines = cell_value.count('\n') + 1  # Учитываем переносы строк
            max_row_height = max(max_row_height, num_lines * 15)  # 15 - приблизительная высота строки
        worksheet.set_row(row_num + 1, max_row_height) # +1, чтобы пропустить заголовки

    # ----------------------- Форматирование строк в зависимости от содержимого ячеек -----------------------
    for row_num in range(len(df)):
        # Проверка столбца "ценность"
        if 'ценность' in df.columns and str(df.loc[row_num, 'ценность']).lower() == 'пусто':
            worksheet.set_row(row_num + 1, options={'hidden': False, 'format': yellow_format}) # +1 для заголовков
            for col_num in range(len(df.columns)):
                worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], yellow_format)

        # Проверка столбца "анализ"
        elif 'анализ' in df.columns and str(df.loc[row_num, 'ценность']).lower() == 'анализ':  # Пример условия
            worksheet.set_row(row_num + 1, options={'hidden': False, 'format': blue_format})# +1 для заголовков
            for col_num in range(len(df.columns)):
                worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], blue_format)

        # Если строка не попадает под условия, добавляем границы
        else:
            for col_num in range(len(df.columns)):
                 worksheet.write(row_num + 1, col_num, df.iloc[row_num, col_num], default_format)


    #  Добавление границ для заголовков
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'border': 1})  # Жирный шрифт + перенос текста + границы
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)


    # Сохраняем файл
    writer.close()
    print(f"DataFrame успешно записан в файл: {filename}")

# ----------------------- Пример использования -----------------------
if __name__ == '__main__':
    # Создаем пример DataFrame
    data = {'Имя': ['Иван', 'Мария', 'Петр', 'Анна'],
            'Возраст': [25, 30, 22, 28],
            'Город': ['Москваыфмврпмвырсмвырмсрпвымспрвмыпр', 'СПб', 'Казань', 'Екб'],
            'ценность': ['Анализ', 'Пусто', 'Анализ', 'Низкая'],
            'анализ': ['Анализ', 'Нет', 'Анализ', 'Нет']}
    df = pd.DataFrame(data)

    # Форматируем и записываем DataFrame в Excel
    format_dataframe_to_excel(df, 'formatted_output.xlsx')