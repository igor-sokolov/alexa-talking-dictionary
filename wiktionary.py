import urllib2
import json
import codecs
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class WiktionaryDictionary:
    url_pattern = 'https://en.wiktionary.org/api/rest_v1/page/definition/{word}'

    def __init__(self):
        self.s = MLStripper()
        self.language = 'en'

    def parse_response(self, response):
        if self.language not in response:
            return {}

        part = response[self.language]
        return {entry['partOfSpeech'].lower(): [strip_tags(i['definition']) for i in entry['definitions']] for entry in
                part}

    def definitions(self, word):
        url = WiktionaryDictionary.url_pattern.format(word=word)
        reader = codecs.getreader("utf-8")
        try:
            response = json.load(reader(urllib2.urlopen(url)))
            return self.parse_response(response)
        except urllib2.HTTPError:
            return {}


if __name__ == '__main__':
    d = WiktionaryDictionary()
    print(d.definitions('control'))
