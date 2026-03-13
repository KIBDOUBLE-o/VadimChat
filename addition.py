import base64
import hashlib
import json
import mimetypes
import os
from threading import Thread
from time import sleep


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

def looks_like(first: str, second: str) -> int:
    u1 = [ord(c) for c in first]
    u2 = [ord(c) for c in second]
    lr = abs(len(u1)-len(u2))
    if lr > 5: return 0
    score = 0
    for i in range(len(u1)):
        if i >= len(u2): continue
        r = abs(u1[i]-u2[i])
        if u1[i]==u2[i]:
            score += 3
        elif r <= 1:
            score += 2
        elif r == 2:
            score += 1
    return (score / lr) if lr != 0 else score

def find_similar(target: str, variants: list) -> str:
    scores = [looks_like(target, variant) for variant in variants]
    _max = 0
    best = -1
    for i in range(len(scores)):
        score = scores[i]
        if score > _max:
            _max = score
            best = i
    if max(scores) < 5 or best == -1: return target
    return variants[best]

def verify_password(stored_hash, password_attempt):
    hash_obj = hashlib.sha256(password_attempt.encode())
    return hash_obj.hexdigest() == stored_hash

def create_secret_key(original) -> str:
    return hashlib.sha256("".join([hex(ord(c)) for c in original]).encode()).hexdigest()

