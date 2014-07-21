#!/usr/bin/env python

# Magica @ 2014-06-30

import re
import sys
import json
import os.path
import traceback
import socket

import torndb
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define('mysql_host', default = '127.0.0.1:3306', help = 'blog database host')
define('mysql_database', default = 'judge', help = 'blog database name')
define('mysql_user', default = 'judge', help = 'blog database user')
define('mysql_password', default = '123456', help = 'blog database password')
define('_user', 'Magica')
define('_name', 'Moe')
define('_secret', 'MagicaCookie')
define('judger_addr', '127.0.0.1:25252')
define('st_name', ['Pending', 'Compilation Error', 'Accepted', 'Unaccepted', # 0 - 3
                   'Running', 'Wrong Answer', # 4 - 5
                   'Runtime Error', 'Floating-point Exception', # 6 - 7
                   'Assertion Failed', 'Segmentation Violation', 'Stack Fault', # 8 - 10
                   'Time Limit Exceeded', 'Memory Limit Exceeded', 'Presentation Error', # 11 - 13
                   'Non-zero Exit Status', 'Output Limit Exceeded', 'Judger Error', # 14 - 16
                   'Interval Error']) # 17

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    def set_default_headers(self):
        self.set_header('Server', 'OnlineJudge')
        self.set_header('X-Frame-Options', 'SAMEORIGIN')
        self.set_header('X-XSS-Protection', '1; mode=block')
        self.set_header('x-content-type-options', 'nosniff')
    def get_current_user(self):
        return self.get_secure_cookie(options._user)
    def get_current_username(self):
        return self.get_secure_cookie(options._name)
    def is_admin(self):
        _info = self.db.get('SELECT admin FROM users WHERE id = %s', self.get_current_user())
        return _info.admin != 0
    def write_error(self, status_code, **kwargs):
        if self.settings.get("debug") and "exc_info" in kwargs:
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            try:
                self.render(str(status_code) + '.html')
            except IOError:
                self.render('500.html')
    def get_username_by_id(self, uid):
        u = self.db.get('SELECT nick FROM users WHERE id = %s', uid)
        return str(u.nick)
    def get_statusname(self, s):
        high = s >> 10;
        low = s - (high << 10);
        if high < 3:
            return '<div class="status-' + str(high) +  '">' + options.st_name[high] + '</div>'
        elif high == 3:
            return '<div class="status-3">' + options.st_name[3] + ': ' + str(low) + '</div>'
        else:
            return '<div class="status-' + str(high) + '">' + options.st_name[high] + ' on case ' + str(low) + '</div>'

class BenchmarkHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello World')

class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html', title = 'Index')

class UserHandler(BaseHandler):
    def get(self, _uid):
        self.render('user.html', uid = _uid)

class UserSignUpHandler(BaseHandler):
    def post(self):
        if self.get_current_user() or self.get_current_username():
            raise tornado.web.HTTPError(403)
        un, pw = self.get_argument('username', None), self.get_argument('password', None)
        ur = re.compile(r'^\S{3,16}$')
        pr = re.compile(r'^[a-f0-9]{32}$')
        if un and pw and ur.match(un) and pr.match(pw):
            e = self.db.get('SELECT * FROM users WHERE lower(name) = %s', un.lower())
            if e:
                self.write('exists')
                return
            self.db.execute('INSERT INTO users (name, nick, password) VALUES (%s, %s, %s)', un, un, pw)
            e = self.db.get('SELECT * FROM users WHERE name = %s', un)
            if not e:
                self.write('error')
            else:
                self.set_secure_cookie(options._user, str(e.id), httponly = True)
                self.set_secure_cookie(options._name, e.nick, httponly = True)
                self.write('ok')
        else:
            raise tornado.web.HTTPError(403)

class UserSignInHandler(BaseHandler):
    def post(self):
        if self.get_current_user() or self.get_current_username():
            raise tornado.web.HTTPError(403)
        un, pw = self.get_argument('username', None), self.get_argument('password', None)
        if un and pw:
            e = self.db.get('SELECT * FROM users WHERE lower(name) = %s AND password = %s', un.lower(), pw)
            if e:
                self.set_secure_cookie(options._user, str(e.id), httponly = True)
                self.set_secure_cookie(options._name, e.nick, httponly = True)
                self.write('ok')
            else:
                self.write('invalid')
        else:
            raise tornado.web.HTTPError(403)

class UserSignOutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(options._user)
        self.clear_cookie(options._name)
        self.write('ok')

class UserUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, _user_id = None):
        if _user_id:
            if not self.is_admin():
                raise tornado.web.HTTPError(403)
        else:
            _user_id = self.get_current_user()
        _user = self.db.get('SELECT * FROM users WHERE id = %s', _user_id)
        self.render('user_update.html', title = 'Update User', user = _user)
    @tornado.web.authenticated
    def post(self, _user_id = None):
        if _user_id:
            if not self.is_admin():
                raise tornado.web.HTTPError(403)
        else:
            _user_id = self.get_current_user()
        nick, pw, admin = self.get_argument('nick', None), self.get_argument('password', None), self.get_argument('admin', None)
        if nick and nick != '' and nick != self.get_current_username():
            self.db.execute('UPDATE users SET nick = %s WHERE id = %s', nick, _user_id)
        if pw and pw != '' and re.compile(r'^[a-f0-9]{32}$').match(pw):
            self.db.execute('UPDATE users SET password = %s WHERE id = %s', pw, _user_id)
        if admin and admin != '':
            self.db.execute('UPDATE users SET admin = %s WHERE id = %s', admin, _user_id)
        self.write('ok')
        if _user_id == self.get_current_user():
            info = self.db.get('SELECT * FROM users WHERE id = %s', _user_id)
            self.set_secure_cookie(options._name, info.nick)

class ProblemHandler(BaseHandler):
    def get(self, prob_id = None):
        if prob_id:
            _prob = self.db.get('SELECT * FROM problems WHERE id = %s', prob_id)
            _uin = self.db.get('SELECT * FROM users WHERE id = %s', self.get_current_user())
            if _prob:
                self.render('problem.html', prob = _prob, title = _prob.name, uin = _uin)
            else:
                raise tornado.web.HTTPError(404)
        else:
            _prob = self.db.query('SELECT * FROM problems LIMIT 100')
            self.render('problist.html', prob = _prob, title = 'Problems')
    @tornado.web.authenticated
    def post(self, prob_id = None):
        if prob_id:
            if not self.db.get('SELECT * FROM problems WHERE id = %s', prob_id):
                raise tornado.web.HTTPError(403)
            self.db.execute('INSERT INTO status (user_id, problem_id, source, compiler) VALUES (%s, %s, %s, %s)', self.get_current_user(), prob_id, self.get_argument('code', None), self.get_argument('lang', None))
            self.db.execute('UPDATE users SET compiler = %s WHERE id = %s', self.get_argument('lang', None), self.get_current_user())
            # Tell Judge Server
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(options.judger_addr)
            sock.sendall('1')
            sock.close()
            self.redirect("/status")
        else:
            raise tornado.web.HTTPError(403)

class StatusHandler(BaseHandler):
    def get(self, run_id = None):
        if not run_id:
            _status = self.db.query('SELECT * FROM status ORDER BY id DESC LIMIT 30')
            self.render('statuslist.html', status = _status, title = 'Status')
        else:
            _info = self.db.get('SELECT * FROM status WHERE id = %s', run_id)
            self.render('status.html', info = _info)

class ApiNavbarHandler(BaseHandler):
    def get(self):
        self.render('navbar.html')

class ApiStatusHandler(BaseHandler):
    def get(self, status_id = None):
        i = self.db.get('SELECT status FROM status WHERE id = %s', status_id)
        self.write(str(i.status))

class ApiResultHandler(BaseHandler):
    def get(self, status_id = None):
        i = self.db.get('SELECT * FROM status WHERE id = %s', status_id)
        self.write(json.dumps(dict(score = i.score, time = i.time, memory = i.memory, msg = i.compilemsg, status = i.status)))

class ApiCodeHandler(BaseHandler):
    def get(self, status_id = None):
        i = self.db.get('SELECT source FROM status WHERE id = %s', status_id)
        self.write(i.source)

class NotFoundHandler(BaseHandler):
    def get(self):
        raise tornado.web.HTTPError(404)
    def post(self):
        raise tornado.web.HTTPError(404)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # Base
            (r'/', IndexHandler),
            (r'/index', IndexHandler),
            # User
            #(r'/user/(\d+)', UserHandler),
            (r'/user/signup', UserSignUpHandler),
            (r'/user/signin', UserSignInHandler),
            (r'/user/signout', UserSignOutHandler),
            (r'/user/update', UserUpdateHandler),
            (r'/user/(\d+)/update', UserUpdateHandler),
            #(r'/user/(\d+)/delete', UserDeleteHandler),
            # Problem
            (r'/problem', ProblemHandler),
            (r'/problem/(\d+)', ProblemHandler),
            #(r'/problem/new', ProblemAddHandler),
            #(r'/problem/(\d+)/update', ProblemUpdateHandler),
            #(r'/problem/(\d+)/delete', ProblemDeleteHandler),
            # Source
            #(r'/source/(\d+)', SourceHandler),
            # Status
            (r'/status', StatusHandler),
            (r'/status/(\d+)', StatusHandler),
            # Contest
            #(r'/contest', ContestHandler),
            #(r'/contest/(\d+)', ContestHandler),
            #(r'/contest/(\d+)/problem/(\w+)', ContestProblemHandler),
            #(r'/contest/(\d+)/board', ContestBoardHandler),
            # Ranklist
            #(r'/ranklist', RanklistHandler),
            # API
            (r'/api/navbar', ApiNavbarHandler),
            (r'/api/status/(\d+)', ApiStatusHandler),
            (r'/api/result/(\d+)', ApiResultHandler),
            (r'/api/code/(\d+)', ApiCodeHandler),
            # Benchmark
            (r'/benchmark', BenchmarkHandler),
            # Not Found
            (r'/.*', NotFoundHandler),
        ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), 'views'),
            static_path = os.path.join(os.path.dirname(__file__), 'public'),
            static_url_prefix = '/public/',
            xsrf_cookies = True,
            cookie_secret = options._secret,
            login_url = "/",
            debug = True,
        )
        tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), 'i18n'))
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = torndb.Connection(
            host = options.mysql_host, database = options.mysql_database,
            user = options.mysql_user, password = options.mysql_password
        )

if __name__ == '__main__':
    port = int(sys.argv[1])
    # tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders = True)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
