#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
from lxml import html
import re

from ...scrapers import Verbix
from ...scraping import register

class VerbixNl(Verbix):

	def __init__(self, word):

		super(VerbixNl, self).__init__(word, 'nl')
		self.tenses['Perfect'] = 'Present Perfect'
		self.tenses['Pluperfect'] = 'Past Perfect'
		self.tenses['Future II'] = 'Future Perfect'

register('nl', VerbixNl)
