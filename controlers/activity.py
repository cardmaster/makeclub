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

class ActivityBase(webapp.RequestHandler):
	def __init__(self, *args, **kw):
		super(ActivityBase, self).__init__(*args, **kw)
		self.actobj = None
		
	def getActModel(self):
		aid, = self.urlcfg.analyze(self.request.path)
		if (aid):
			id = int(aid)
			return Activity.get_by_id(id)
		else:
			return None
	def actionPath(self):
		return self.request.path
	def templateParams(self):
		act = self.actobj
		club = act.club
		cluburl = urldict['ClubView'].path(club.slug)
		templateVars = dict(club = club, cluburl = cluburl, act = act, action = self.actionPath() )
		return templateVars
	def makeResponseText(self, act):
		templateVars = self.templateParams()
		return render(self.template, templateVars)
	def checkPrivilige(self):
		user = get_current_user()
		if (not user):
			errorPage ("Not login", create_login_url(self.request.url), self.response, 403)
			return False
		if (not hasActPrivilige(user, self.actobj, self.actOperation)):
			errorPage ("Not authorrized", 
					urldict['ClubVew'].getPath(self.actobj.club.slug), 
					self.response, 403)
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


class ActivityView(ActivityBase):
	def __init__(self, *args, **kw):
		super (ActivityView, self).__init__(*args, **kw)
		self.template = 'activity_view.html'
		self.urlcfg = urldict['ActivityView']
		self.actOperation = "view"
	def templateParams(self):
		defaults = super (ActivityView, self).templateParams()
		if (hasActPrivilige(get_current_user(), self.actobj, "edit" )):
			defaults['editurl'] = urldict['ActivityEdit'].path(self.actobj.key().id() )
		return defaults
	
class ActivityJoin(webapp.RequestHandler):
	def get(self, *args):
		pass

def extractRequestData(request, interested):
	retval = dict()
	for (key, valid) in interested.iteritems() :
		val = valid (request.get(key))
		if (val):
			retval [key] = val
	return retval

import re
def parseDuration(times):
	 #support only h
	 tstr = times[:-1]
	 print "Times String: ", tstr
	 return float(tstr)
	
def parseBill (billstr):
	entries = billstr.split (',')
	ary = []
	i = 1
	for ent in entries:
		if (i == 2):
			val = ent
			ary.push ( (key, val) )
			i = 0
		else :
			key = ent
		i += 1
	return ary

class ActivityEdit(ActivityBase):
	def __init__(self, *args, **kw):
		super (ActivityEdit, self).__init__(*args, **kw)
		self.template = 'activity_edit.html'
		self.urlcfg = urldict['ActivityEdit']
		self.actobj = None
		self.actOperation = "edit"
	def updateObject(self, actobj):
		interested = dict (name = str, intro = str, duration = parseDuration, bill = parseBill)
		reqs = extractRequestData (self.request, interested)
		for (key, val) in reqs.iteritems():
			setattr (actobj, key, val)
		#Will read data from postdata, and update the pass-in actobj.
		pass
	def post(self, *args):
		actobj = self.getActModel()
		if (actobj):
			self.actobj = actobj
			if (self.checkPrivilige()):
				self.updateObject(actobj)
				key = actobj.put()
				if (key):
					return errorPage("Successfully storing this Activity", 
									urldict['ActivityView'].path(key.id()), self.response, 200)
				else:
					return errorPage("Error while storing this Activity", 
									urldict['ActivityEdit'].path(actobj.key().id()), self.response, 501)
		else:
			return errorPage("No such Activity", urldict['ClubList'].path(), self.response, 404)

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
