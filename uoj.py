#!/usr/bin/env python

# Magica @ 2014-06-30

import re
import os.path
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
        return self.get_secure_cookie('Magica')
    def get_current_username(self):
        return self.get_secure_cookie('Moe')

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
        pr = re.compile(r'^[a-f0-9]{32}')
        if un and pw and ur.match(un) and pr.match(pw):
            e = self.db.get("SELECT * FROM users WHERE lower(name) = %s", un.lower())
            if e:
                self.write('exists')
                return
            self.db.execute("INSERT INTO users (name, password) VALUES (%s, %s)", un, pw)
            e = self.db.get("SELECT * FROM users WHERE name = %s", un)
            if not e:
                self.write('error')
            else:
                self.set_secure_cookie('Magica', str(e.id))
                self.set_secure_cookie('Moe', e.name)
                self.write('ok')
        else:
            raise tornado.web.HTTPError(403)

class UserSignInHandler(BaseHandler):
    def post(self):
        if self.get_current_user() or self.get_current_username():
            raise tornado.web.HTTPError(403)
        un, pw = self.get_argument('username', None), self.get_argument('password', None)
        if un and pw:
            e = self.db.get("SELECT * FROM users WHERE lower(name) = %s AND password = %s", un.lower(), pw)
            if e:
                self.set_secure_cookie('Magica', str(e.id))
                self.set_secure_cookie('Moe', e.name)
                self.write('ok')
            else:
                self.write('invalid')
        else:
            raise tornado.web.HTTPError(403)

class UserSignOutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('Magica')
        self.clear_cookie('Moe')
        self.write('ok')

class ApiNavbarHandler(BaseHandler):
    def get(self):
        self.render('navbar.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # Base
            (r'/', IndexHandler),
            (r'/index', IndexHandler),
            # User
            #(r'/user/(d+)', UserHandler),
            (r'/user/signup', UserSignUpHandler),
            (r'/user/signin', UserSignInHandler),
            (r'/user/signout', UserSignOutHandler),
            #(r'/user/update', UserUpdateHandler),
            #(r'/user/(d+)/update', UserUpdateHandler),
            #(r'/user/(d+)/delete', UserDeleteHandler),
            # Problem
            #(r'/problem', ProblemHandler),
            #(r'/problem/(d+)', ProblemHandler),
            #(r'/problem/new', ProblemAddHandler),
            #(r'/problem/(d+)/update', ProblemUpdateHandler),
            #(r'/problem/(d+)/delete', ProblemDeleteHandler),
            # Source
            #(r'/source/(d+)', SourceHandler),
            # Status
            #(r'/status', StatusHandler),
            #(r'/status/(d+)', StatusHandler),
            # Contest
            #(r'/contest', ContestHandler),
            #(r'/contest/(d+)', ContestHandler),
            #(r'/contest/(d+)/problem/(\w+)', ContestProblemHandler),
            #(r'/contest/(d+)/board', ContestBoardHandler),
            # Ranklist
            #(r'/ranklist', RanklistHandler),
            # API
            (r'/api/navbar', ApiNavbarHandler),
        ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), 'views'),
            static_path = os.path.join(os.path.dirname(__file__), 'public'),
            static_url_prefix = '/public/',
            xsrf_cookies = True,
            cookie_secret = 'Magica',
            login_url = "/auth/login",
            debug = True,
        )
        tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), 'i18n'))
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = torndb.Connection(
            host = options.mysql_host, database = options.mysql_database,
            user = options.mysql_user, password = options.mysql_password
        )

if __name__ == '__main__':
    port = [5555, 6666, 7777, 8888]
    tornado.options.parse_command_line()
    for p in port:
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(p)
    tornado.ioloop.IOLoop.instance().start()
