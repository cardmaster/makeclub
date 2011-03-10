from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Club
import os

class ClubEdit(webapp.RequestHandler):
	def __init__(self, 
			template=os.path.join(os.path.dirname(__file__), '../templates/default/clubedit.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.clubmodel = None
		self.template = template
	
	def accessControl(self):
		user = users.get_current_user()
		if user:
			pass
		else:
			self.redirect(users.create_login_url(self.request.uri))
		return user

	def responseClub(self, clubmodel, nickname):
		templateValues = dict(action=self.request.path, username=nickname, model=clubmodel)
		if (clubmodel.is_saved()):
			templateValues['oldslug'] = clubmodel.slug
		self.response.out.write (template.render(self.template, templateValues) )

	def makeClubModel(self, slug=''):
		if (not slug):
			slug = self.request.get('slug', '')
		if (slug):
			return Club.getClub(slug)
		return Club()

	def analyzePath(self):
		path = self.request.path
		try:
			slashIndex = path.rindex('/')
			slug = path[slashIndex + 1:]
		except:
			slug = ''
		finally:
			return slug

	def get(self):
		user = self.accessControl()
		if (self.clubmodel):
			clubmd=self.clubmodel
		else: 
			clubmd = self.makeClubModel(self.analyzePath())
		self.responseClub (clubmd, user.nickname())

	def parsePostdata(self, request, oldslug=''):
		owner = request.get('owner', self.accessControl() )
		if (not oldslug):
			oldslug = request.get('oldslug', '')
		slug = request.get('slug', '')
		if (not slug):
			return False
		name = request.get('name', '')
		fund = request.get('fund', '')
		intro = request.get('intro', '')
		if (oldslug):#in edit mode
			clubmd = self.makeClubModel(oldslug)
		else:        #Create new model
			clubmd = self.makeClubModel(slug)
		clubmd.slug = slug
		clubmd.name = name
		clubmd.fund = fund
		clubmd.intro = intro
		return clubmd

	def post(self): 
		pathslug=self.analyzePath()
		clubmd = self.parsePostdata (self.request, pathslug)
		if (clubmd): #Put valid, then redirect
			self.clubmodel = clubmd
			clubmd.put()
			self.redirect ("/club/edit/" + clubmd.slug)
		else:
			self.get()

	def put(self):
		self.response.set_status(404)
		self.response.write ("Not supported put interface")

