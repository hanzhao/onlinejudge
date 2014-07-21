#!/usr/bin/env pypy

import sys

inp, outp, std = sys.argv[1], sys.argv[2], sys.argv[3]

#### Normal Judge
o = open(outp)
s = open(std)
flag = True
while True:
    x = o.readline()
    y = s.readline()
    if not x and not y:
        break
    if not x or not y or x != y:
        flag = False
        break
o.close()
s.close()

if flag:
    print 10
    sys.exit(0)

#### Advance Judge
o = open(outp)
s = open(std)
flag = True
while True:
    x = ''
    while x is '':
        x = o.readline().strip()
    y = ''
    while y is '':
        y = s.readline().strip()
    if not x and not y:
        break
    if not x or not y or x != y:
        flag = False
        break
o.close()
s.close()

if flag:
    print 10
    sys.exit(0)
else:
    print 0
    sys.exit(0)
