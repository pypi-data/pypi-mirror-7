#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


class API(object):
    """API"""
    def __init__(self, shanbay):
        self.shanbay = shanbay
        self.request = shanbay.request

    @property
    def user_info(self):
        url = 'http://www.shanbay.com/api/user/info/'
        return self.request(url).json()

    def query_word(self, word):
        url = 'http://www.shanbay.com/api/word/%s' % quote(word)
        return self.request(url).json()

    def add_word(self, word):
        url = 'http://www.shanbay.com/api/learning/add/%s' % word
        return self.request(url).json()

    def examples(self, learn_id):
        url = 'http://www.shanbay.com/api/learning/examples/%s'
        url = url % learn_id
        return self.request(url).json()

    def add_example(self, learn_id, question, answer):
        url = 'http://www.shanbay.com/api/example/add/%s?sentence=%s&translation=%s'
        url = url % (learn_id, quote(question.encode('utf8')),
                     quote(answer.encode('utf8')))
        return self.request(url).json()

    def add_note(self, learn_id, note):
        url = 'http://www.shanbay.com/api/note/add/%s?note=%s'
        url = url % (learn_id, quote(note.encode('utf8')))
        return self.request(url).json()
