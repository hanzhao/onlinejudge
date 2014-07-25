#!/usr/bin/env pypy

import os
import sys
import math
from resource import *

lang, inp, time = sys.argv[1], sys.argv[2], int(sys.argv[3])

cmd = { 'C': './Main',
        'Cpp': './Main',
        'Cpp11': './Main',
        'Pascal': './Main',
        'Java': 'java',
        'Python': 'python',
        'PyPy': './Main.py',
        'Ruby': 'ruby' }
argv = { 'C': '',
        'Cpp': '',
        'Cpp11': '',
        'Pascal': '',
        'Java': 'Main',
        'Python': 'Main.pyc',
        'PyPy': '',
        'Ruby': 'Main.rb' }
"""
env = { 'GEM_PATH': '/home/magimagi/.rvm/gems/ruby-2.1.2:/home/magimagi/.rvm/gems/ruby-2.1.2@global',
        'PATH': '/home/magimagi/.pyenv/shims:/home/magimagi/.pyenv/bin:/home/magimagi/.rvm/gems/ruby-2.1.2/bin:/home/magimagi/.rvm/gems/ruby-2.1.2@global/bin:/home/magimagi/.   rvm/rubies/ruby-2.1.2/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/home/magimagi/.local/bin:/home/magimagi/.rvm/bin',
        'GEM_HOME': '/home/magimagi/.rvm/gems/ruby-2.1.2' }
"""

pid = os.fork()
if pid == 0:
    infd = os.open(inp, os.O_RDONLY);
    os.dup2(infd, 0)
    os.close(infd)
    outfd = os.open('_tmp_output', os.O_WRONLY | os.O_CREAT);
    os.dup2(outfd, 1)
    os.close(outfd)
    errfd = os.open('_tmp_errmsg', os.O_WRONLY | os.O_CREAT);
    os.dup2(errfd, 2)
    os.close(errfd)
    setrlimit(RLIMIT_CPU, (time + 1, time + 1))
    os.execvpe(cmd[lang], ('', argv[lang]), {'': ''})
    sys._exit(255)
else:
    _, status, usage = os.wait4(RUSAGE_CHILDREN, os.WUNTRACED)
    print os.WIFEXITED(status), os.WEXITSTATUS(status), os.WIFSIGNALED(status), os.WTERMSIG(status), os.WCOREDUMP(status), usage.ru_utime + usage.ru_stime, (usage.ru_maxrss if usage.ru_maxrss <= 16000 else usage.ru_maxrss - 16000)
