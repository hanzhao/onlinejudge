#!/usr/bin/env pypy

import os
import sys
import math
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

prob_dir = os.getcwd() + '/problems/' + str(status.problem_id)

# Temp Directory
dir_name = './tmp/judge_' + str(run_id)
compile_msg = None
if os.path.exists(dir_name):
    rmtree(dir_name)
os.mkdir(dir_name)
copy('./runner.py', dir_name)
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
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
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
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
elif lang == 'Pascal':
    f = open('Main.pas', 'w')
    f.write(source)
    f.close()
    # Pascal Compile
    cmd = 'fpc Main.pas -Sd -O2 -Op2 -dONLINE_JUDGE'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
elif lang == 'Java':
    f = open('Main.java', 'w')
    f.write(source)
    f.close()
    # Java Compile
    cmd = 'javac Main.java'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
elif lang == 'Python':
    f = open('Main.py', 'w')
    f.write(source)
    f.close()
    # Syntax Check & Compile
    cmd = 'python -m py_compile Main.py'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
elif lang == 'PyPy':
    f = open('Main.py', 'w')
    f.write(source)
    f.close()
    # Syntax Check & Compile
    cmd = 'pypy -m py_compile Main.py'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    # Compile Error
    if p.returncode != 0:
        state = 1 << 10
elif lang == 'Ruby':
    f = open('Main.rb', 'w')
    f.write(source)
    f.close()
    # Syntax Check
    cmd = 'ruby -c Main.rb'
    p = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE)
    p.wait()
    compile_msg = p.stderr.read()
    # Syntax Error
    if p.returncode != 0:
        state = 1 << 10
if state == 1 << 10:
    db.execute('UPDATE statis SET status = %s, compilemsg = %s WHERE id = %s', state, compile_msg, run_id)
    sys.exit(0)

################
# Prepare Data
################
for name in glob(prob_dir + '/*'):
    copy(name, './')

config = open('config', 'r')
for line in config:
    inp, outp, time_limit, score = line.split('|')
    cmd = ' '.join(['./runner.py', lang, inp, 'tmp_output', str(int(math.ceil(float(time_limit))))])
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
    p.wait()
    returncode, exited, timeused, memoryused = p.stdout.read().split()
    returncode = int(returncode)
    exited = bool(exited)
    timeused = float(timeused)
    memoryused = int(memoryused)
    # TODO
config.close()

status = db.execute('UPDATE status SET status = %s, compilemsg = %s WHERE id = %s', state, compile_msg, run_id)
