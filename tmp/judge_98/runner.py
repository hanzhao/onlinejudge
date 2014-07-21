#!/usr/bin/env pypy

import os
import sys
import math
from resource import *

lang, inp, outp, time = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
cmd = { 'C': './Main',
        'Cpp': './Main',
        'Cpp11': './Main',
        'Pascal': './Main',
        'Java': '/usr/bin/java',
        'Python': '/usr/bin/python',
        'PyPy': '/home/magimagi/.local/pypy-2.3.1-linux64/bin/pypy',
        'Ruby': '/home/magimagi/.rvm/rubies/ruby-2.1.2/bin/ruby' }
argv = { 'C': '',
         'Cpp': '',
         'Cpp11': '',
         'Pascal': '',
         'Java': 'Main',
         'Python': 'Main.pyc',
         'PyPy': 'Main.pyc',
         'Ruby': 'Main.rb' }
pid = os.fork()
if pid == 0:
    infd = os.open(inp, os.O_RDONLY);
    os.dup2(infd, 0)
    os.close(infd)
    outfd = os.open(outp, os.O_WRONLY | os.O_CREAT);
    os.dup2(outfd, 1)
    os.close(outfd)
    setrlimit(RLIMIT_CPU, (time + 1, time + 1))
    os.execv(cmd[lang], [''])
    sys._exit(255)
else:
    _, status, usage = os.wait4(RUSAGE_CHILDREN, os.WUNTRACED)
    print os.WIFEXITED(status), os.WEXITSTATUS(status), os.WIFSIGNALED(status), os.WTERMSIG(status), os.WCOREDUMP(status), usage.ru_utime + usage.ru_stime, (usage.ru_maxrss if usage.ru_maxrss <= 17312 else usage.ru_maxrss - 17312)
