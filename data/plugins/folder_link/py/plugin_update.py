import os
import hashlib
from time import sleep


# -------------------------- UTILS --------------------------

def hash_file(path: str) -> str | None:
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


def read_file(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""


def scan_folder(path: str) -> dict:
    data = {"dirs": {}, "files": {}}

    try:
        entries = os.listdir(path)
    except Exception:
        return data

    for entry in entries:
        full = os.path.join(path, entry)

        if os.path.isdir(full):
            data["dirs"][entry] = scan_folder(full)
        else:
            data["files"][entry] = hash_file(full)

    return data


# -------------------------- DIFF --------------------------

def diff_folders(path, old, new, send_func):

    old_files = old.get("files", {})
    new_files = new.get("files", {})
    old_dirs = old.get("dirs", {})
    new_dirs = new.get("dirs", {})

    # --- FILES ---

    # Удалённые
    for name in old_files:
        if name not in new_files:
            send_func("file_deleted", os.path.join(path, name), "")

    # Новые
    for name in new_files:
        if name not in old_files:
            full = os.path.join(path, name)
            send_func("new_file", full, read_file(full))

    # Изменённые
    for name in new_files:
        if name in old_files and new_files[name] != old_files[name]:
            full = os.path.join(path, name)
            send_func("file_changed", full, read_file(full))

    # --- DIRECTORIES ---

    # Удалённые
    for name in old_dirs:
        if name not in new_dirs:
            send_func("dir_deleted", os.path.join(path, name), "")

    # Новые
    for name in new_dirs:
        if name not in old_dirs:
            full = os.path.join(path, name)
            send_func("new_dir", full, "")
            push_full_folder(full, send_func)

    # Рекурсивное сравнение
    for name in new_dirs:
        if name in old_dirs:
            diff_folders(os.path.join(path, name),
                         old_dirs[name], new_dirs[name], send_func)


# -------------------------- PUSH FULL TREE --------------------------

def push_full_folder(path, send_func):
    try:
        entries = os.listdir(path)
    except Exception:
        return

    for entry in entries:
        full = os.path.join(path, entry)

        if os.path.isdir(full):
            send_func("new_dir", full, "")
            push_full_folder(full, send_func)
        else:
            send_func("new_file", full, read_file(full))

# -------------------------- MAIN BLOCK --------------------------

# Загружаем состояние всех папок
states = self.callback.get_data("folderlink/states", {})

def flsend(t, target, data):
    self.callback.send_uni(f"{t}:{target}:{data}", 'any', 'folderlink')

if self.folderlink:
    updated = 0

    for folder_path in self.folders.keys():

        new_state = scan_folder(folder_path)
        old_state = states.get(folder_path)

        # Первая синхронизация
        if old_state is None:
            states[folder_path] = new_state

        else:
            diff_folders(
                folder_path,
                old_state,
                new_state,
                lambda t, path, content: flsend(t, path, content)
            )
            states[folder_path] = new_state

        updated += 1

    # Сохраняем обновлённое состояние всех папок
    self.callback.save_data("folderlink/states", states)

    print(f"[OK] Plugin update: {updated} folders updated! total: {len(self.folders)}")
