"""
The main GAE script.

@author: Michael Hausenblas, http://sw-app.org/mic.xhtml#i
@since: 2011-06-11
@status: inital version
"""
import sys
import os
import logging
import cgi
import platform

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '0.96')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from handler import *


application = webapp.WSGIApplication([
						(r'/translate', LowLevelHandler),
						(r'/(.+)/(.+)/$', FromToHandler),
						(r'/mdpretty', MicrodataPrettyPrintHandler),
						(r'/', MainHandler),
						(r'/.*', NotFoundHandler)
					],
					debug=False)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
	main()
