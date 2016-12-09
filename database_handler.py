import MySQLdb
import logging
import os

__author__ = 'bwire'

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

log = logging.getLogger("tornado.application")


class WordStore:
    database = None

    def __init__(self, hashing_salt, encryption_key):

        self.hashing_salt = hashing_salt
        self.encryption_key = encryption_key

    def connect_to_cloudsql(self):
        # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
        # will be set to 'Google App Engine/version'.
        if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
            # Connect using the unix socket located at
            # /cloudsql/cloudsql-connection-name.
            cloudsql_unix_socket = os.path.join(
                '/cloudsql', CLOUDSQL_CONNECTION_NAME)

            db = MySQLdb.connect(
                unix_socket=cloudsql_unix_socket,
                user=CLOUDSQL_USER,
                passwd=CLOUDSQL_PASSWORD)
        else:
            db = MySQLdb.connect(
                host='127.0.0.1', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

        return db

    def initialize_tables(self):

        database = self.connect_to_cloudsql()
        cursor = database.cursor()
        # cursor.execute("CREATE DATABASE IF NOT EXISTS octopus;")
        cursor.execute("USE octopus;")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS crawled_words ( WORD_KEY VARBINARY(64) NOT NULL, WORD VARBINARY(255) NOT NULL, WORD_COUNT INT DEFAULT 1, PRIMARY KEY (WORD_KEY) );")
        database.close()

    def get_database_cursor(self):

        if not self.database:
            self.database = self.connect_to_cloudsql()

        cursor = self.database.cursor()
        cursor.execute("USE octopus;")
        return cursor

    def save(self, word, count):

        cursor = self.get_database_cursor()

        try:

            # We insert since word is not already in the database.
            insert_query = "INSERT INTO crawled_words(WORD_KEY, WORD, WORD_COUNT) VALUES (UNHEX(SHA2(CONCAT('%s','%s'), 256)), AES_ENCRYPT('%s','%s'), %d ) ON DUPLICATE KEY UPDATE WORD_COUNT=WORD_COUNT+%d" % (
            word, self.hashing_salt, word, self.encryption_key, count, count)
            cursor.execute(insert_query)

            # Commit your changes in the database
            self.database.commit()

        except Exception as e:

            log.error(" accessing the database ", exc_info=True)

            # Rollback in case there is any error
            self.database.rollback()

    def cleanup(self):

        if self.database:
            self.database.close()

    def list_stored_stuff(self):

        cursor = self.get_database_cursor()

        word_exists_query = "SELECT HEX(WORD_KEY), AES_DECRYPT(WORD, '%s' ), WORD_COUNT FROM crawled_words ORDER BY WORD_COUNT DESC" % (self.encryption_key)
        cursor.execute(word_exists_query)

        results = cursor.fetchall()

        return results
