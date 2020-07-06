# coding=utf-8

import errno
import os
import shutil
import stat


def handle_remove_readonly(func, path, exc):
    """Remove readonly status of given path and run func onto this path.

    Args:
        func:
        path:
        exc:

    Returns:

    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def hotfix(source_folder, dest_folder):
    for folder, sub, files in os.walk(source_folder):
        dest_path = folder.replace(source_folder, dest_folder)
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)
        for _file in files:
            shutil.copy2(os.path.join(folder, _file),
                         os.path.join(dest_path, _file))
