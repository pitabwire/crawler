#!/usr/bin/env python
#

import logging
import os

import tornado
import tornado.web
import tornado.ioloop
import tornado.wsgi

import wsgiref.handlers

from database_handler import WordStore
from handler import MainHandler, AdminHandler

HASHING_SALT = os.environ.get('HASHING_SALT')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')


log = logging.getLogger("tornado.general")


settings = {
    "crawler_title_up": u"Crawler",
    "crawler_title": u"Octopus Investment test",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "xsrf_cookies": True,
    "debug": True,
    "autoreload": False
}

logging.basicConfig()

# setup database.
word_store_ = WordStore(hashing_salt=HASHING_SALT, encryption_key=ENCRYPTION_KEY)
word_store_.initialize_tables()

application = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
    ('/', MainHandler),
    ('/admin/', AdminHandler),

], **settings)

application = tornado.wsgi.WSGIAdapter(application)
