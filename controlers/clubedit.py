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
from google.appengine.api import users
from google.appengine.ext import webapp

from models import Club, Membership
from template import render
from errors import errorPage
from infopage import infoPage
from access import hasClubPrivilige, isAccessible
from helper import splitPath
from url import urldict

class ClubEdit(webapp.RequestHandler):
	def __init__(self, 
			template='clubedit.html', *args, **kw ):
		self.urlconf = urldict['ClubEdit']
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.clubmodel = None
		self.template = template
	
	def accessControl(self):
		user = users.get_current_user()
		if user:
			return (True, user)
		else:
			return (False, users.create_login_url(self.request.uri))

	def responseClub(self, clubmodel, nickname):
		templateValues = dict(action=self.request.path, username=nickname, model=clubmodel)
		if (hasClubPrivilige(users.get_current_user(), clubmodel, "finance" )):
			templateValues['enableFinance'] = True
		if (clubmodel.is_saved()):
			templateValues['oldslug'] = clubmodel.slug
		self.response.out.write (render(self.template, templateValues, self.request.url) )

	def makeClubModel(self, slug=''):
		if (not slug):
			slug = self.request.get('slug', '')
		if (slug):
			return Club.getClub(slug)
		return Club()

	def analyzePath(self):
		path = self.request.path
		slug, = self.urlconf.analyze(path)
		return slug

	def editOrCreateRight(self, user, club):
		if ( (not club.is_saved() and isAccessible (user, "createClub"))  #Create
				or (club.is_saved() and hasClubPrivilige(user, club, "edit")) ): #Edit
			return True
		else:
			errorPage( self.response,  "Access Deny For club",   users.create_login_url(self.request.uri))#Access Deny
			return False

	def get(self, *args):
		stat, user = self.accessControl()
		if (not stat):
			return errorPage( self.response,   "User %s Not Log in" % user,  users.create_login_url(self.request.uri))
		if (self.clubmodel):
			clubmd=self.clubmodel
		else: 
			clubmd = self.makeClubModel(self.analyzePath())
		if (not clubmd.is_saved()):
			clubmd.owner = user
		if (self.editOrCreateRight(user, clubmd)):
			self.responseClub (clubmd, user.nickname())

	def parsePostdata(self, request, oldslug=''):
		owner = request.get('owner', users.get_current_user() )
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
		clubmd.owner = owner
		clubmd.slug = slug
		clubmd.name = name
		if (hasClubPrivilige(users.get_current_user(), clubmd, "finanace" )):
			clubmd.fund = fund
		clubmd.intro = intro
		return clubmd

	def post(self, *args): 
		stat, user = self.accessControl()
		pathslug=self.analyzePath()
		clubmd = self.parsePostdata (self.request, pathslug)
		if (clubmd): #Put valid, then redirect
			if ( self.editOrCreateRight(user, clubmd) ):
				self.clubmodel = clubmd
				isNewClub = not clubmd.is_saved()
				clubmd.put()
				if (isNewClub): #Create New Membership For Owner when create the club
					mem = Membership(user=user, club = clubmd)
					mem.put()
				infoPage (self.response, "Successfullyt Saved Club", "Club Saved", urldict['ClubView'].path(clubmd.slug))
			else:
				return
		else:
			self.get()

	def put(self, *args):
		self.response.set_status(404)
		self.response.write ("Not supported put interface")
