from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import os

class ClubEdit(webapp.RequestHandler):
	def __init__(self, 
			template=os.path.join(os.path.dirname(__file__), '../templates/default/clubedit.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template
	
	def accessControl(self):
		user = users.get_current_user()
		if user:
			pass
		else:
			self.redirect(users.create_login_url(self.request.uri))
		return user

	def responseClub(clubmodel, nickname):
		templateValues = dict(action=self.request.uri, username=nickname, model=clubmodel)
		self.response.out.write (template.render(self.template, templateValues) )

	def get(self):
		user = self.accessControl()

	def post(self): 
		self.get()

	def put(self):
		self.response.set_status(404)
		self.response.write ("Not supported put interface")

