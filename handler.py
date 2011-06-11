"""
The handler script.

@author: Michael Hausenblas, http://sw-app.org/mic.xhtml#i
@since: 2011-06-11
@status: inital version
"""
import sys
sys.path.insert(0, 'lib')
import logging
import cgi
import os
import platform
import urllib
import urllib2
import StringIO
import csv

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import rdflib

from rdflib import Graph
from rdflib import Namespace
from rdflib import plugin
from rdflib.serializer import Serializer

import schema_org_processor


class MainHandler(webapp.RequestHandler):
	def get(self):
		self.response.out.write(template.render('index.html', None))

class NotFoundHandler(webapp.RequestHandler):
	def get(self):
		self.error(404)
		self.response.out.write(template.render('a404.html', None))

class SchemaOrgHandler(webapp.RequestHandler):
	def get(self, doc_url):
		logging.info('Trying to translate document at [%s]' %(urllib.unquote(doc_url)))
		
		try:
			sop = schema_org_processor.SchemaOrgProcessor()
			sop.parse(urllib.unquote(doc_url))
			self.response.headers.add_header("Access-Control-Allow-Origin", "*") # CORS-enabled
			self.response.headers['Content-Type'] = 'application/rdf+xml'
			self.response.out.write(str(sop.dump_data()))
		except Exception, e:
			self.error(404)
			self.response.out.write(e)#template.render('a404.html', None))