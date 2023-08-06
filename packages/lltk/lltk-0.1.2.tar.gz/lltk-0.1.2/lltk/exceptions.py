#!/usr/bin/python
# -*- coding: UTF-8 -*-

class LanguageNotSupported(Exception):
	''' Used to indicate that a certain language is not supported. '''
	pass

class GoingTooFast(Exception):
	''' Used to pause scraping when there are too many queries within a short time. '''
	pass

class IncorrectForvoAPIKey(Exception):
	''' Used when you provide a wrong API key for forve audiosamples. '''
	pass

class DailyForvoLimitExceeded(Exception):
	''' Used when the daily Forvo API limit is exceeded. '''
	pass
