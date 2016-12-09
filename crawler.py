#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging
import os
import wsgiref.simple_server
import tornado
import tornado.web
import tornado.wsgi

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
    "debug": True
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
#
# server = wsgiref.simple_server.make_server('', 8888, application)
# server.serve_forever()

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()

