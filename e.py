import ftplib
import os
from smb.SMBConnection import SMBConnection
import logging
import datetime
from smb.base import SMBServerNameResolver

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FTPtoSMBTransfer:
    """
    Класс для скачивания файлов с FTP и загрузки их на SMB-сервер.
    """

    def __init__(self, ftp_host, ftp_user, ftp_password, ftp_source_dir,
                 smb_host, smb_share, smb_user, smb_password, smb_dest_dir,
                 local_temp_dir="/tmp/ftp_to_smb", delete_ftp_after_transfer=False):
        """
        Инициализирует объект FTPtoSMBTransfer.

        Args:
            ftp_host (str): Адрес FTP-сервера.
            ftp_user (str): Имя пользователя FTP.
            ftp_password (str): Пароль FTP.
            ftp_source_dir (str): Исходная директория на FTP.
            smb_host (str): Адрес SMB-сервера.
            smb_share (str): Имя общего ресурса (share) на SMB.
            smb_user (str): Имя пользователя SMB.
            smb_password (str): Пароль SMB.
            smb_dest_dir (str): Целевая директория на SMB.
            local_temp_dir (str, optional): Локальная временная директория. Defaults to "/tmp/ftp_to_smb".
            delete_ftp_after_transfer (bool, optional): Удалять ли файлы с FTP после успешной передачи. Defaults to False.
        """
        self.ftp_host = ftp_host
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.ftp_source_dir = ftp_source_dir
        self.smb_host = smb_host
        self.smb_share = smb_share
        self.smb_user = smb_user
        self.smb_password = smb_password
        self.smb_dest_dir = smb_dest_dir
        self.local_temp_dir = local_temp_dir
        self.delete_ftp_after_transfer = delete_ftp_after_transfer
        self.conn = None  # SMB connection
        self.ftp = None  # FTP connection
        os.makedirs(self.local_temp_dir, exist_ok=True)  # Создаем локальную временную директорию
        self.server_name_resolver = SMBServerNameResolver(self.smb_host, is_direct_tcp=True)


    def connect_smb(self):
        """Подключается к SMB-серверу."""
        try:
            #client_name = "FTPSMBClient"[:15]  # Имя должно быть не длиннее 15 символов
            #self.conn = SMBConnection(self.smb_user, self.smb_password, client_name, self.smb_host, use_ntlm_v2=True, is_direct_tcp=True)
            #if self.conn.connect(self.smb_host, 445):
            resolved_server_names = self.server_name_resolver.resolve()
            if len(resolved_server_names) > 0:
                self.conn = SMBConnection(self.smb_user, self.smb_password, "client_name", resolved_server_names[0], use_ntlm_v2=True, is_direct_tcp=True)
                if self.conn.connect(resolved_server_names[0], 445):
                    logging.info(f"Успешно подключились к SMB: {self.smb_host}/{self.smb_share}")
                    return True
                else:
                    logging.error(f"Не удалось подключиться к SMB: {self.smb_host}/{self.smb_share}")
                    return False
            else:
                logging.error(f"Не удалось разрешить имя SMB-сервера: {self.smb_host}")
                return False

        except Exception as e:
            logging.error(f"Ошибка при подключении к SMB: {e}")
            return False

    def connect_ftp(self):
        """Подключается к FTP-серверу."""
        try:
            self.ftp = ftplib.FTP(self.ftp_host)
            self.ftp.login(self.ftp_user, self.ftp_password)
            self.ftp.cwd(self.ftp_source_dir)
            logging.info(f"Успешно подключились к FTP: {self.ftp_host}/{self.ftp_source_dir}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при подключении к FTP: {e}")
            return False

    def transfer_files(self):
        """
        Скачивает файлы с FTP, сохраняет их локально, а затем загружает на SMB.
        """
        if not self.connect_ftp():
            logging.error("Не удалось установить соединение с FTP.")
            return

        if not self.connect_smb():
            logging.error("Не удалось установить соединение с SMB.")
            self.ftp.quit()
            return

        try:
            files = self.ftp.nlst()  # Get file list
            logging.info(f"Найдено {len(files)} файлов на FTP")

            for filename in files:
                #Проверяем, что это файл, а не директория
                try:
                    self.ftp.sendcmd(f'MDTM {filename}')
                except ftplib.error_perm as e:
                    if str(e).startswith('550'):
                        logging.info(f"Пропускаем, т.к. это не файл: {filename}")
                        continue
                    else:
                        raise

                local_filepath = os.path.join(self.local_temp_dir, filename)
                smb_filepath = os.path.join(self.smb_dest_dir, filename)

                logging.info(f"Скачиваем с FTP: {filename} -> {local_filepath}")
                try:
                    with open(local_filepath, 'wb') as local_file:
                        self.ftp.retrbinary(f'RETR {filename}', local_file.write)
                    logging.info(f"Файл успешно скачан: {filename}")
                except Exception as e:
                    logging.error(f"Ошибка при скачивании файла {filename}: {e}")
                    continue

                logging.info(f"Загружаем на SMB: {local_filepath} -> {self.smb_share}/{smb_filepath}")
                try:
                    with open(local_filepath, 'rb') as local_file:
                        # Изменено storeFile для работы с директориями SMB
                        try:
                            self.conn.storeFile(self.smb_share, smb_filepath, local_file)
                            logging.info(f"Файл успешно загружен на SMB: {filename}")
                        except Exception as smb_e:
                            logging.error(f"Ошибка при записи файла {filename} на SMB: {smb_e}")

                except Exception as e:
                    logging.error(f"Ошибка при загрузке файла {filename} на SMB: {e}")

                # Удаление файла с FTP (если требуется)
                if self.delete_ftp_after_transfer:
                    try:
                        self.ftp.delete(filename)
                        logging.info(f"Файл успешно удален с FTP: {filename}")
                    except Exception as e:
                        logging.error(f"Ошибка при удалении файла {filename} с FTP: {e}")

                # Clean up local file
                try:
                    os.remove(local_filepath)
                    logging.info(f"Временный файл успешно удален: {local_filepath}")
                except OSError as e:
                    logging.error(f"Ошибка при удалении временного файла {local_filepath}: {e}")

        except Exception as e:
            logging.error(f"Произошла общая ошибка: {e}")
        finally:
            if self.ftp:
                self.ftp.quit()
                logging.info("Соединение с FTP закрыто.")
            if self.conn:
                self.conn.close()
                logging.info("Соединение с SMB закрыто.")

# ----------------------- Пример использования -----------------------
if __name__ == "__main__":
    # Замените значения на ваши
    ftp_host = "your_ftp_host"
    ftp_user = "your_ftp_user"
    ftp_password = "your_ftp_password"
    ftp_source_dir = "/path/to/ftp/source"
    smb_host = "your_smb_host"
    smb_share = "your_smb_share"
    smb_user = "your_smb_user"
    smb_password = "your_smb_password"
    smb_dest_dir = "/path/to/smb/destination"

    transfer = FTPtoSMBTransfer(
        ftp_host=ftp_host,
        ftp_user=ftp_user,
        ftp_password=ftp_password,
        ftp_source_dir=ftp_source_dir,
        smb_host=smb_host,
        smb_share=smb_share,
        smb_user=smb_user,
        smb_password=smb_password,
        smb_dest_dir=smb_dest_dir,
        delete_ftp_after_transfer=False  # Измените на True, если хотите удалять файлы с FTP
    )

    transfer.transfer_files()