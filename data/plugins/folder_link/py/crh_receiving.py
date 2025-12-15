import os
import shutil

if data_type == '[folderlink]':
    data = full_message.split(':', 2)

    t = data[0]
    target = data[1]
    other = data[2] if len(data) > 2 else ""

    dirname = os.path.dirname(target)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)

    if t == "new_file":
        open(target, "w", encoding="utf-8").write(other)

    elif t == "file_changed":
        open(target, "w", encoding="utf-8").write(other)

    elif t == "file_deleted":
        if os.path.exists(target):
            os.remove(target)

    elif t == "new_dir":
        os.makedirs(target, exist_ok=True)

    elif t == "dir_deleted":
        if os.path.exists(target):
            shutil.rmtree(target)
