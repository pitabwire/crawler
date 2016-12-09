import re
from bs4 import BeautifulSoup

__author__ = 'bwire'


class DictionaryBuilder:

    def __clean_html(self, html_text):

        if html_text:
            return BeautifulSoup(html_text).get_text()

        else:
            return None

    def process(self, html_page):

        cleaned_words = self.__clean_html(html_text=html_page)

        page_dictionary = dict()

        for word in re.sub("[^\w]", " ",  cleaned_words).split():

            if word.isalpha():
                if word in page_dictionary:
                    page_dictionary[word] += 1

                else:
                    page_dictionary[word] = 1

        sorted_list = sorted(page_dictionary.items(), key=lambda value: value[1])

        #Only keep top 100
        return sorted_list[-100:]
