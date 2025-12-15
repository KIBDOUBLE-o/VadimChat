import base64
import json
import mimetypes
import os


def get_key(d: dict, value): return next(k for k, v in d.items() if v == value)

def pack_file(file_path: str) -> str:
    if not os.path.isfile(file_path):
        return ""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{encoded}"
    #print(f"PACKED FILE: {data_uri}")
    return data_uri

def save_base64_to_file(base64_string: str, save_dir: str, filename: str):
    """
    Сохраняет файл из base64 строки по указанному пути.

    :param base64_string: строка в формате base64
    :param save_dir: директория для сохранения файла
    :param filename: имя файла с расширением (например, "image.png" или "data.txt")
    :return: полный путь к сохранённому файлу
    """
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, filename)

    if "," in base64_string:
        base64_string = base64_string.split(",", 1)[1]

    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_string))

    return file_path