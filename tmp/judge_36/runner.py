#!/usr/bin/env python

import os
import sys
import math
from resource import *

lang, inp, outp, time = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])

if lang == 'C' or lang == 'Cpp' or lang == 'Cpp11' or lang == 'Pascal':
    pid = os.fork()
    if pid == 0:
        infd = os.open(inp, os.O_RDONLY);
        os.dup2(infd, 0)
        os.close(infd)
        outfd = os.open(outp, os.O_WRONLY | os.O_CREAT);
        os.dup2(outfd, 1)
        os.close(outfd)
        print time
        setrlimit(RLIMIT_CPU, (time, time))
        os.execv('./Main', [''])
        sys._exit(255)
    else:
        _, status, usage = os.wait4(pid, os.WUNTRACED)
        print os.WEXITSTATUS(status), os.WIFEXITED(status), usage.ru_utime + usage.ru_stime, usage.ru_minflt * getpagesize() >> 10

