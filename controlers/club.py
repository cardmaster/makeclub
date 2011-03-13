'''Copyright(C): Leaf Johnson 2011

    This file is part of makeclub.

    makeclub is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    makeclub is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with makeclub.  If not, see <http://www.gnu.org/licenses/>.

 
 
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Club
import os

class ClubList(webapp.RequestHandler):
	def __init__(self,
			template=os.path.join(os.path.dirname(__file__), '../templates/default/clublist.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template

	def get(self, *args):
		clubs = Club.all()
		cluburl = "/club"
		self.response.out.write (template.render(self.template, locals()) )

class ClubView(webapp.RequestHandler):
	def __init__(self, 
			template=os.path.join(os.path.dirname(__file__), '../templates/default/clubview.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template

	def get(self, *args):
		self.response.out.write (template.render(self.template, locals()) )

