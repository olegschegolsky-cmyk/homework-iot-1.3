import csv
import os
import logging

class FileCorrupted(Exception):
    pass

class FileNotFound(Exception):
    pass

def logged(exc_cls, mode):
    def decorator(func):
        def wrapers(*args, **kwargs):
            logger = logging.getLogger("LabLogger")
            logger.setLevel(logging.ERROR)
            

            if mode == "file":
                handler = logging.FileHandler("log.txt", mode='a', encoding='utf-8')
            else:
                handler = logging.StreamHandler()

            if logger.hasHandlers():
                logger.handlers.clear()

            
            format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(format)
            logger.addHandler(handler)
            
            try:
                return func(*args, **kwargs)
            except exc_cls as e:
                logger.error(f"помилка в {func.__name__}: {e}")
                raise e
        return wrapers
    return decorator

class Csv:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            raise FileNotFound(f"файл не знайдено: {self.path}")

    @logged(FileCorrupted, "console")
    def read(self):
        try:
            with open(self.path, 'r', newline='', encoding='utf-8') as f:
                return list(csv.reader(f))
        except (OSError, csv.Error) as e:
            raise FileCorrupted(f"файл пошкоджено: {e}")

    @logged(FileCorrupted, "file")
    def write(self, data):
        try:
            with open(self.path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(data)
        except OSError as e:
            raise FileCorrupted(f"помилка запису: {e}")

    @logged(FileCorrupted, "file")
    def append(self, data):
        try:
            with open(self.path, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(data)
        except OSError as e:
            raise FileCorrupted(f"помилка дописування: {e}")


try:
    manager = Csv("data.csv")
    manager.write([["Name", "Group"]])
    manager.write([["Oleg", "IR-11"]])
    manager.append([["Hanna", "IR-12"]])
    manager.append([["Bodia", "IR-12"]])
    print(manager.read())
except (FileNotFound, FileCorrupted) as e:
    print(f"виняток: {e}")