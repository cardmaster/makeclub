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

from google.appengine.api.users import get_current_user, create_login_url
from google.appengine.ext import webapp
from google.appengine.ext import db
from errors import errorPage
from access import hasActPrivilige, hasClubPrivilige
from models import Activity, Membership, Club
from url import urldict
from template import render

class ActivityView(webapp.RequestHandler):
	def get(self, *args):
		pass

class ActivityJoin(webapp.RequestHandler):
	def get(self, *args):
		pass

class ActivityEdit(webapp.RequestHandler):
	def __init__(self, *args, **kw):
		super (ActivityEdit, self).__init__(*args, **kw)
		self.template = 'activity_edit.html'
		self.urledit = urldict['ActivityEdit']
		self.actobj = None
	def getActModel(self):
		aid, = self.urledit.analyze(self.request.path)
		if (aid):
			id = int(aid)
			return Activity.get_by_id(id)
		else:
			return None
	def actionPath(self):
		return self.request.path
	def makeResponseText(self, act):
		club = act.club
		cluburl = urldict['ClubView'].path(club.slug)
		templateVars = dict(club = club, cluburl = cluburl, act = act, action = self.actionPath() )
		return render(self.template, templateVars)
	def checkPrivilige(self):
		user = get_current_user()
		if (not user):
			errorPage ("Not login", create_login_url(self.request.url), self.response, 403)
			return False
		if (not hasActPrivilige(user, self.actobj, "edit")):
			errorPage ("Not Authorized to edit", urldict['ClubVew'].getPath(self.actobj.club.slug), self.response, 403)
			return False
		return True
			
	def get(self, *args):
		actobj = self.getActModel()
		if (actobj):
			self.actobj = actobj
			if (self.checkPrivilige()):
				self.response.out.write (self.makeResponseText(actobj))
			else:
				return
		else:
			return errorPage("No such Activity", urldict['ClubList'].path(), self.response, 404)
	def post(self, *args):
		print "Handling Post"
		print self.request

class ActivityNew(ActivityEdit):
	def getActModel(self):
		urlcfg = urldict['ActivityNew']
		slug, = urlcfg.analyze(self.request.path)
		user = get_current_user()
		club = Club.getClubBySlug(slug)
		if (user and club):
			newact = Activity.createDefault(user, club)
			if (newact): newact.bill = [('Filed Expense', 80), ('Balls Expense', 30)]
			return newact
		else:
			return None
	def checkPrivilige(self):
		user = get_current_user()
		if (not user):
			errorPage ("Not login", create_login_url(self.request.url), self.response, 403)
			return False
		if (not hasClubPrivilige(user, self.actobj.club, "newact")):
			errorPage ("Not Authorized to edit", urldict['ClubVew'].getPath(self.actobj.club.slug), self.response, 403)
			return False
		return True
	def get(self, *args):
		super (ActivityNew, self).get(*args)
