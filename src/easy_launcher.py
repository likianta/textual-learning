"""
automatically add paths to sys.path then launch target file.

cmd:
    python3 easy_launcher.py <target_py_file>
"""
import os
import sys

current_dir = os.path.abspath('.')  # -> `~/src`
sys.path.append(current_dir)
sys.path.append(current_dir + '/examples')

target = current_dir + '/' + sys.argv[1]
target_dir = os.path.dirname(target)
sys.path.append(target_dir)

os.chdir(target_dir)
with open(target, 'r', encoding='utf-8') as f:
    exec(f.read(), globals(), locals())
