"""
automatically add paths to sys.path then launch target file.

cmd:
    python3 run_example.py <target>
        target: the *relative path* to a '.py' file. the path is relative to
        current folder (~/examples).
        
example:
    python3 run_example.py filezen/fence.py
"""
import os
import sys

from lk_utils import relpath

sys.path.append(relpath('.'))
sys.path.append(relpath('../src'))  # add `textual_extensions` to sys.path

target = relpath(sys.argv[1])
target_dir = os.path.dirname(target)
sys.path.append(target_dir)

os.chdir(target_dir)
with open(target, 'r', encoding='utf-8') as f:
    exec(f.read(), globals(), locals())
