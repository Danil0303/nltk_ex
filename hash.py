import os
import hashlib
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_file_hash(filepath, block_size=65536):
    """Вычисляет SHA-256 хеш файла."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as file:
            while True:
                block = file.read(block_size)
                if not block:
                    break
                hasher.update(block)
        return hasher.hexdigest()
    except FileNotFoundError:
        logging.error(f"Файл не найден: {filepath}")
        return None
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {filepath}: {e}")
        return None


def find_duplicate_files(root_dir):
    """
    Ищет дубликаты файлов в заданной директории и ее поддиректориях.

    Args:
        root_dir (str): Корневая директория для поиска.

    Returns:
        dict: Словарь, где ключи - хеши файлов, а значения - списки путей к файлам с этим хешом.
    """
    file_hashes = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            file_hash = calculate_file_hash(filepath)

            if file_hash:
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(filepath)
                else:
                    file_hashes[file_hash] = [filepath]
    return file_hashes


def delete_duplicate_files(file_hashes):
    """
    Удаляет дубликаты файлов, оставляя только один оригинал.

    Args:
        file_hashes (dict): Словарь хешей файлов и списков путей к файлам.

    """
    duplicates_found = False
    for file_hash, filepaths in file_hashes.items():
        if len(filepaths) > 1:
            duplicates_found = True
            logging.info(f"Найдены дубликаты файлов с хешем: {file_hash}")
            # Сохраняем первый файл, удаляем остальные
            original_file = filepaths[0]
            logging.info(f"Сохраняем оригинал: {original_file}")

            for duplicate_file in filepaths[1:]:
                logging.info(f"Дубликат для удаления: {duplicate_file}")
                try:
                    os.remove(duplicate_file)
                    logging.info(f"Файл удален: {duplicate_file}")
                except Exception as e:
                    logging.error(f"Ошибка при удалении файла {duplicate_file}: {e}")

    if not duplicates_found:
        logging.info("Дубликаты файлов не найдены.")


if __name__ == "__main__":
    root_directory = "C:\\Projects\\nltk_ex\\78"
    

    file_hashes = find_duplicate_files(root_directory)
    delete_duplicate_files(file_hashes)

    logging.info("Процесс завершен.")
