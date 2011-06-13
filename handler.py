"""
The handler script.

@author: Michael Hausenblas, http://sw-app.org/mic.xhtml#i
@since: 2011-06-11
@status: integrated working version of SchemaOrgProcessor
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
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import rdflib

from rdflib import Graph
from rdflib import Namespace
from rdflib import plugin
from rdflib.serializer import Serializer

import schema_org_processor
import microdata_pp

# for RDF/JSON output:
plugin.register("rdf-json-pretty", Serializer, "rdfjson.RdfJsonSerializer", "PrettyRdfJsonSerializer")
plugin.register("json-ld", Serializer, "rdfjson.JsonLDSerializer", "JsonLDSerializer")

class MainHandler(webapp.RequestHandler):
	def get(self):
		self.response.out.write(template.render('index.html', None))

class NotFoundHandler(webapp.RequestHandler):
	def get(self):
		self.error(404)
		self.response.out.write(template.render('a404.html', None))

class LowLevelHandler(webapp.RequestHandler):
	def get(self):
		doc_url = urllib.unquote(self.request.get('url'))
		out_format = self.request.get('format')
		logging.info('Trying to translate document at [%s]' %doc_url)

		# the following is a nasty hack - SOP should take care of it
		if doc_url.endswith('/'): doc_url = doc_url + "index.html"
		sop = schema_org_processor.SchemaOrgProcessor()
		
		try:
			sop.parse(doc_url) # parse input, guessing format
			self.response.headers.add_header("Access-Control-Allow-Origin", "*") # CORS-enabled API
			self.response.headers['Content-Type'] = 'text/turtle'
			self.response.out.write(str(sop.dump_data(format='turtle')))
		except Exception, e:
			self.error(404)
			self.response.out.write(e)
			
	def _parse_from_to(self, from_param, to_param):
		in_format = from_param
		out_format = to_param
		return (in_format, out_format)

class FromToHandler(webapp.RequestHandler):
	INPUTFORMATS = [
		'microdata',
		'csv'
	]
	
	OUTFORMATS = {
		'rdf-xml' : 'application/rdf+xml' ,
		'rdf-turtle' : 'text/turtle',
		'json' : 'application/json'
	}
	
	
	def get(self, from_param, to_param):
		in_format, out_format, out_mediatype = self._parse_params(from_param, to_param)
		doc_url = self.request.get('url')
		
		if not doc_url:
			self._list_from_to()
		else:
			logging.info('Trying to translate document [%s] from: %s to: %s' %(doc_url, from_param, to_param))
	
			# the following is a nasty hack - SOP should take care of it
			if doc_url.endswith('/'): doc_url = doc_url + "index.html"
			sop = schema_org_processor.SchemaOrgProcessor()

			try:
				self.response.headers.add_header("Access-Control-Allow-Origin", "*") # CORS-enabled API
			
				if out_mediatype:
					if in_format in FromToHandler.INPUTFORMATS: # supported input format
						parse_status = sop.parse(doc_url, input_format=in_format) # try to parse input and convert to RDF
						if parse_status: # parsing was successful
							logging.info('Translating input format %s to output format %s' %(in_format, out_format))
							self.response.headers['Content-Type'] = out_mediatype
							if out_format == 'rdf-xml':
								r = sop.dump_data(format='xml')
								if r: self.response.out.write(str(r))
								else:
									logging.info('ERROR outputting %s' %out_format)
									self._error_translating()
							elif out_format == 'rdf-turtle':
								r = sop.dump_data(format='turtle')
								if r: self.response.out.write(str(r))
								else:
									logging.info('ERROR outputting %s' %out_format)
									self._error_translating()
							elif out_format == 'json':
								self.response.out.write(str(sop.get_data().serialize(None, "json-ld")))
								#r = sop.get_data().serialize(format="json-ld")
								#r = sop.dump_data(format="rdf-json-pretty")
								# if r:
								# 	self.response.out.write(str(r))
								# else:
								# 	logging.info('ERROR outputting %s - got %s' %(out_format, r))
								# 	self._error_translating()
						else:
							logging.info('Parsing input format %s was not successful' %(in_format))
							self._error_translating()
					else: # unsupported input format
						logging.info('Wrong or unsupported input format %s ...' %(in_format))
						self._error_translating()
				else:
					logging.info('Wrong or unsupported output format %s ...' %(out_format))
					self._error_translating()
			except Exception, e:
				#self.response.out.write(e)
				self._error_translating()

	def _parse_params(self, from_param, to_param):
		in_format = from_param
		out_format = to_param
		try:
			out_mediatype = FromToHandler.OUTFORMATS[str(out_format)]
		except:
			out_mediatype = None
		return (in_format, out_format, out_mediatype)
	
	def _list_from_to(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('INPUT FORMATS:\n')
		for f in FromToHandler.INPUTFORMATS:
			self.response.out.write(" " + f + "\n")
		self.response.out.write('\nOUTPUT FORMATS:\n')
		for f in FromToHandler.OUTFORMATS:
			self.response.out.write(" " + f + " (served as: %s) "%FromToHandler.OUTFORMATS[f] + "\n")

	def _error_translating(self):
		self.error(404)
		self.response.out.write(template.render('a404.html', None))

class MicrodataPrettyPrintHandler(webapp.RequestHandler):
	def get(self):
		doc_url = urllib.unquote(self.request.get('url'))
		logging.info('Trying to pretty-print HTML+microdata document at [%s]' %doc_url)
		
		try:
			mdp = microdata_pp.MicrodataPrettyPrinter()
			mdp.items_from_URL(doc_url)
			self.response.headers.add_header("Access-Control-Allow-Origin", "*") # CORS-enabled
			# self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write(str(mdp.dump_items()))
		except Exception, e:
			self.error(404)
			self.response.out.write(e)