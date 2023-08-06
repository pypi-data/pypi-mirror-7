#!/usr/bin/python
# -*- coding: UTF-8 -*-

__all__ = ['scrapers', 'scrape', 'conjugate']

import scrapers
from ..scraping import scrape
from ..decorators import language

ISO639_1 = 'fr'
scrape = language(ISO639_1)(scrape)

def conjugate(word, tense):
	''' Returns the conjugation of a given verb. '''
	return scrape('conjugate', word, tense)
