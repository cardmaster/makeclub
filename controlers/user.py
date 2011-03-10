from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import os

class UserList(webapp.RequestHandler):
	def __init__(self,
			template=os.path.join(os.path.dirname(__file__), '../templates/default/userlist.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template

	def get(self):
		self.response.out.write (template.render(self.template, locals()) )

class UserView(webapp.RequestHandler):
	def __init__(self, 
			template=os.path.join(os.path.dirname(__file__), '../templates/default/userview.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template

	def get(self):
		self.response.out.write (template.render(self.template, locals()) )

