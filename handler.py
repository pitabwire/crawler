import functools
import logging
import os
import requests
from google.appengine.api import users
import tornado.web
from database_handler import WordStore
from word_handler import DictionaryBuilder

__author__ = 'bwire'

HASHING_SALT = os.environ.get('HASHING_SALT')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

log = logging.getLogger("tornado.application")


def administrator(method):
    """Decorate with this method to restrict to site admins."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                self.redirect("/")
                return
            raise tornado.web.HTTPError(403)
        elif not self.current_user.administrator:
            if self.request.method == "GET":
                self.redirect("/")
                return
            raise tornado.web.HTTPError(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(tornado.web.RequestHandler):
    """Implements Google Accounts authentication methods."""
    def get_current_user(self):
        user = users.get_current_user()
        if user:
            user.administrator = users.is_current_user_admin()
        return user

    def get_login_url(self):
        return users.create_login_url(self.request.uri)

    def get_template_namespace(self):
        # Let the templates access the users module to generate login URLs
        ns = super(BaseHandler, self).get_template_namespace()
        ns['users'] = users
        return ns


class AdminHandler(BaseHandler):

    @administrator
    def get(self, *args, **kwargs):

        word_store = WordStore(hashing_salt=HASHING_SALT, encryption_key=ENCRYPTION_KEY)
        word_results = word_store.list_stored_stuff()

        self.render("admin.html", results=word_results)


class MainHandler(BaseHandler):

    def get(self):

        self.render("index.html", )

    def post(self, *args, **kwargs):

        crawled_url = self.get_argument("url_to_be_crawled")

        try:

            r = requests.get(crawled_url, verify=False)
            r.raise_for_status()

            response = r.text
            # successfully fetched page.

            dict_builder = DictionaryBuilder()
            sorted_list = dict_builder.process(html_page=response)

            word_store = WordStore(hashing_salt=HASHING_SALT, encryption_key=ENCRYPTION_KEY)

            for word, count in sorted_list:
                word_store.save(word=word, count=count)

            word_store.cleanup()

            self.render("results.html", crawled_url=crawled_url, sorted_list=sorted_list)

        except Exception as e:
            log.warn(" problems while processing ", exc_info=True)
            self.render("index.html", error_message="Could not successfully fetch page : %s" % crawled_url)

