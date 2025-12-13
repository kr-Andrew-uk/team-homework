import os
import json
import logging
from functools import wraps

class FileNotFound(Exception):
    pass

class FileCorrupted(Exception):
    pass


def logged(exception_type, mode="file"):
    def decorator(func):

        logger = logging.getLogger(func.__name__)
        logger.setLevel(logging.ERROR)

        if not logger.hasHandlers():
            if mode == "console":
                handler = logging.StreamHandler()
            else:
                handler = logging.FileHandler("log.txt", encoding="utf-8")

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except exception_type as e:
                logger.error(f"{exception_type.__name__}: {str(e)}")
                raise

        return wrapper
    return decorator



class JsonFileManager:

    @logged(FileNotFound, mode="file")
    def __init__(self, path: str):
        self.path = path

        if not os.path.exists(self.path):
            raise FileNotFound(f"Файл '{self.path}' не існує.")

    @logged(FileCorrupted, mode="file")
    def read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise FileCorrupted(f"Неможливо прочитати файл '{self.path}': {e}")

    @logged(FileCorrupted, mode="file")
    def write(self, data):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise FileCorrupted(f"Помилка запису у файл '{self.path}': {e}")

    @logged(FileCorrupted, mode="file")
    def append(self, new_data):

        try:
            if os.path.getsize(self.path) == 0:
                data = []
            else:
                data = self.read()
            if not isinstance(data, list):
                data = [data]
            data.append(new_data)
            self.write(data)

        except Exception as e:
            raise FileCorrupted(f"Помилка дописування у файл '{self.path}': {e}")


if __name__ == "__main__":
    try:
        manager = JsonFileManager("data.json")

        print("Поточні дані:", manager.read())

        manager.append({"dsfdsfds": 123})

    except Exception as err:
        print("Виключення:", err)
