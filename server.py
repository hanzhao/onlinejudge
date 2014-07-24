#!/usr/bin/env pypy

import sys
import socket
import traceback
import subprocess

import torndb

# MySQL Settings
mysql_host = '127.0.0.1:3306'
mysql_database = 'judge'
mysql_user = 'judge'
mysql_password = '123456'

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind('127.0.0.1:25252')
sock.listen(5)

Judging = False
Wating = False

while True:
    if Wating:
        Wating = False
        db = torndb.Connection(mysql_host, mysql_database, mysql_user, mysql_password, max_idle_time = 5)
        db._ensure_connected()
        status = db.query('SELECT * FROM status WHERE status = %s ORDER BY id ASC', 0)
        Judging = True
        for s in status:
            p = subprocess.Popen('./judger.py ' + str(s.id), shell=True)
            p.wait()
        Judging = False
        continue
    connection, address = sock.accept()
    try:
        connection.settimeout(20)
        buf = connection.recv(4096)
        # New Judge Request
        if buf == '1':
            if Judging:
                Waiting = True
                continue
            db = torndb.Connection(mysql_host, mysql_database, mysql_user, mysql_password, max_idle_time = 5)
            db._ensure_connected()
            status = db.query('SELECT * FROM status WHERE status = %s ORDER BY id ASC', 0)
            Judging = True
            for s in status:
                p = subprocess.Popen('./judger.py ' + str(s.id), shell=True)
                p.wait()
            Judging = False
    except socket.timeout:
        print 'Timeout'
        pass
    except (KeyboardInterrupt, SystemExit):
        raise
    connection.close()

