import csv
import os
import logging
import functools

class FileCorrupted(Exception):
    pass

class FileNotFound(Exception):
    pass

def get_logger(mode):
    logger_name = "LabLogger_File" if mode == "file" else "LabLogger_Console"
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        if mode == "file":
            handler = logging.FileHandler("log.txt", mode='a', encoding='utf-8')
        else:
            handler = logging.StreamHandler()
            
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def logged(exc_cls, mode):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(mode) 
            try:
                return func(*args, **kwargs)
            except exc_cls as e:
                logger.error(f"помилка в {func.__name__}: {e}")
                raise e
        return wrapper
    return decorator

class Csv:
    def __init__(self, path):
        self.path = path

    @logged(FileCorrupted, "console")
    def read(self):
        if not os.path.exists(self.path):
            raise FileNotFound(f"файл не знайдено: {self.path}")
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
    if not os.path.exists("data.csv"):
        manager.write([["Name", "Group"]])
    else:
        print("файл вже існує, додаю нові дані")

    manager.append([["Oleg", "IR-11"]])
    manager.append([["Hanna", "IR-12"]])
    manager.append([["Bodia", "IR-12"]])
    
    print(manager.read())
except (FileNotFound, FileCorrupted) as e:
    print(f"виняток: {e}")