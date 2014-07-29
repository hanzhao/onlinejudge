#!/usr/bin/env pypy

import os
import sys
import math
import signal
import subprocess
import torndb
from glob import *
from shutil import rmtree, copy

# MySQL Settings
mysql_host = '127.0.0.1:3306'
mysql_database = 'judge'
mysql_user = 'judge'
mysql_password = '123456'

db = torndb.Connection(mysql_host, mysql_database, mysql_user, mysql_password, max_idle_time = 5)
db._ensure_connected()

run_id = int(sys.argv[1])
status = db.get('SELECT * FROM status WHERE id = %s', run_id)
prob = db.get('SELECT * FROM problems WHERE id = %s', status.problem_id)

lang = status.compiler
source = status.source
kind = prob.kind
state = 0

root_dir = os.getcwd()
runner_dir = os.getcwd() + '/runners'
prob_dir = os.getcwd() + '/problems/' + str(status.problem_id)

# Temp Directory
dir_name = './tmp/judge_' + str(run_id)
compile_msg = None
if os.path.exists(dir_name):
    rmtree(dir_name)
os.mkdir(dir_name)
# copy('./runner.py', dir_name)
if not prob.sj:
    copy('./comparer', dir_name)
os.chdir(dir_name)

################
# Begin Compile
################
if lang == 'C':
    f = open('Main.c', 'w')
    f.write(source)
    f.close()
    # C compile
    cmd = 'gcc -o Main Main.c -fno-asm -O2 -Wall -lm --static -DONLINE_JUDGE'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/c_runner', './runner')
elif lang == 'Cpp' or lang == 'Cpp11':
    f = open('Main.cpp', 'w')
    f.write(source)
    f.close()
    # C++ Compile
    cmd = 'g++ -o Main Main.cpp -fno-asm -O2 -Wall -lm --static -DONLINE_JUDGE'
    if lang == 'Cpp11':
        cmd = cmd + ' -std=c++11'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/cpp_runner', './runner')
elif lang == 'Pascal':
    f = open('Main.pas', 'w')
    f.write(source)
    f.close()
    # Pascal Compile
    cmd = 'fpc Main.pas -Sd -O2 -Op2 -dONLINE_JUDGE'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/pas_runner', './runner')
elif lang == 'Java':
    f = open('Main.java', 'w')
    f.write(source)
    f.close()
    # Java Compile
    cmd = 'javac Main.java'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/java_runner', './runner')
elif lang == 'Python':
    f = open('Main.py', 'w')
    f.write("#!/usr/bin/env python\n")
    f.write(source)
    f.close()
    # Syntax Check & Compile
    cmd = 'chmod +x Main.py'
    p = subprocess.Popen(cmd, shell = True)
    p.wait()
    cmd = 'python -m py_compile Main.py'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/py_runner', './runner')
elif lang == 'PyPy':
    f = open('Main.py', 'w')
    f.write("#!/usr/bin/env pypy\n")
    f.write(source)
    f.close()
    # Syntax Check & Compile
    cmd = 'chmod +x Main.py'
    p = subprocess.Popen(cmd, shell = True)
    p.wait()
    cmd = 'pypy -m py_compile Main.py'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/pypy_runner', './runner')
elif lang == 'Ruby':
    f = open('Main.rb', 'w')
    f.write("#!/usr/bin/env ruby\n")
    f.write(source)
    f.close()
    # Syntax Check
    cmd = 'chmod +x Main.rb'
    p = subprocess.Popen(cmd, shell = True)
    p.wait()
    cmd = 'ruby -c Main.rb'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    p.stderr.close()
    # Syntax Error
    if p.returncode != 0:
        state = 1 << 10
    else:
        copy(runner_dir + '/rb_runner', './runner')
if state == 1 << 10:
    db.execute('UPDATE status SET status = %s, compilemsg = %s WHERE id = %s', state, compile_msg, run_id)
    sys.exit(0)
else:
    db.execute('UPDATE status SET compilemsg = %s WHERE id = %s', compile_msg, run_id)

################
# Prepare Data
################
for name in glob(prob_dir + '/*'):
    copy(name, './')


config = open('config', 'r')
case = 0
total = 0
totaltime = 0.0
totalmem = 0
ACFlag = True
for line in config:
    case += 1
    inp, outp, time_limit, score = line.split('|')
    cmd = ' '.join(['./runner', lang, inp, str(int(math.ceil(float(time_limit))))])
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, close_fds = True)
    state = 4 << 10
    db.execute('UPDATE status SET status = %s WHERE id = %s', state + case, run_id)
    p.wait()
    exited, exitstatus, signaled, termsig, dumped, timeused, memoryused = p.stdout.read().split()
    p.stdout.close()
    exited = (exited == "True") or (exited == "1")
    exitstatus = int(exitstatus)
    signaled = (signaled == "True") or (exited == "1")
    termsig = int(termsig)
    dumped = (dumped == "True") or (exited == "1")
    timeused = float(timeused)
    memoryused = int(memoryused)
    totaltime = totaltime + timeused
    totalmem = max(memoryused, totalmem)
    ###################
    # Judge
    ###################
    if dumped: # Runtime Error
        if signaled and termsig == signal.SIGSEGV: # Segmentation Violation
            state = 9 << 10
        elif signaled and termsig == signal.SIGFPE: # Floating-point Exception
            state = 7 << 10
        elif signaled and termsig == 16: # Stack Fault
            state = 10 << 10
        elif signaled and termsig == 6:
            state = 8 << 10
        else: # Runtime Error
            state = 6 << 10
    elif timeused > float(time_limit): # Time Limit Exceeded
        state = 11 << 10
    elif memoryused > prob.memorylimit: # Memory Limit Exceeded
        state = 12 << 10
    elif not exited: # Runtime Error
        state = 6 << 10
    elif exitstatus != 0: # Non-zero Exit Status
        state = 14 << 10
    else:
        cmd = ' '.join(['./comparer', inp, outp, '_tmp_output'])
        p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, close_fds = True)
        p.wait()
        msg = int(p.stdout.read())
        p.stdout.close()
        if msg == 0: # Wrong Answer
            state = 5 << 10
        elif msg == 1: # Presentation Error
            state = 13 << 10
        else: # Accepted!
            state = 2 << 10
            total += int(score)
    if state != 4 << 10 and state != 2 << 10:
        db.execute('UPDATE status SET status = %s WHERE id = %s', state + case, run_id)
        if kind == 0: # ACM Mode, Stop.
            ACFlag = False
            break
    if os.path.exists('_tmp_output'):
        os.remove('_tmp_output')
    if kind == 1 and os.path.exists('_tmp_errmsg'):
        os.remove('_tmp_errmsg')
config.close()
if ACFlag and total >= 100:
    db.execute('UPDATE status SET status = %s, time = %s, memory = %s, score = %s WHERE id = %s', 2 << 10, totaltime, totalmem, total, run_id)
elif kind == 1: # OI Mode
    db.execute('UPDATE status SET status = %s, time = %s, memory = %s, score = %s WHERE id = %s', (3 << 10) + total, totaltime, totalmem, total, run_id)

os.chdir(root_dir)
if os.path.exists(dir_name):
    rmtree(dir_name)

