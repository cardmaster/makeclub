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

from google.appengine.api.users import get_current_user, create_login_url, User
from google.appengine.ext import webapp
from google.appengine.ext import db
from errors import errorPage
from infopage import infoPage
from access import hasActPrivilige, hasClubPrivilige
from models import Activity, Membership, Club, ActivityParticipator
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
		return render(self.template, templateVars, self.request.url)
	def checkPrivilige(self):
		user = get_current_user()
		if (not user):
			errorPage ( self.response,  "Not login",   create_login_url(self.request.url),   403)
			return False
		if (not hasActPrivilige(user, self.actobj, self.actOperation)):
			errorPage ( 					self.response,  "Not authorrized",   					urldict['ClubView'].path(self.actobj.club.slug),   403)
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
			return errorPage( self.response,  "No such Activity",   urldict['ClubList'].path(),   404)

class SpecialOp:
	def __init__(self, oper = '', url = '', needPost = False, data = [], display = ''):
		self.oper = oper
		if (not display):
			display = oper
		self.display = display
		self.url = url
		self.needPost = needPost
		self.data = data

class ActivityView(ActivityBase):
	def __init__(self, *args, **kw):
		super (ActivityView, self).__init__(*args, **kw)
		self.template = 'activity_view.html'
		self.urlcfg = urldict['ActivityView']
		self.actOperation = "view"
	def templateParams(self):
		defaults = super (ActivityView, self).templateParams()
		user = get_current_user();
		aid = self.actobj.key().id()
		specialOps = []
		if (hasActPrivilige(user, self.actobj, "edit" )):
			sop = SpecialOp('edit', urldict['ActivityEdit'].path(aid), False)
			specialOps.append(sop)
		urlcfg = urldict['ActivityParticipate']
		for oper in ('bill', 'join', 'quit', 'confirm'):
			if (hasActPrivilige(user, self.actobj, oper) ):
				data = [('target', user.email()), ]
				sop = SpecialOp(oper, urlcfg.path(aid, oper), True, data)
				specialOps.append(sop)
		defaults['specialOps'] = specialOps
		
		participatorOps = []
		for oper in ('confirm', ):
			if (hasActPrivilige(user, self.actobj, oper) ):
				sop = SpecialOp(oper, urlcfg.path(aid, oper), True, [])
				participatorOps.append(sop)
		defaults['participatorOps'] = participatorOps
		apq = ActivityParticipator.all()
		apq.filter ('activity = ', self.actobj)
		defaults['participators'] = apq
		return defaults
	
class ActivityParticipate(webapp.RequestHandler):
	def getActModel(self, id):
		try:
			iid = int(id)
		except:
			return None
		actobj = Activity.get_by_id(iid)	
		return actobj
	def get(self, *args):
		urlcfg = urldict['ActivityParticipate']
		id, oper = urlcfg.analyze(self.request.path)
		self.response.out.write ( 
			'on id %s, operation %s' % (id, oper)
		)
	def post(self, *args):
		urlcfg = urldict['ActivityParticipate']
		id, oper = urlcfg.analyze(self.request.path)
		id = int(id)
		actobj = self.getActModel(id)
		if (not actobj):
			return errorPage (self.response,  urldict['ClubList'].path(),  "No such activity",  404 )
		user = get_current_user();
		if (not user):
			return errorPage ( self.response,  "Not login",   create_login_url(self.request.url),   403)
		target = self.request.get ('target')
		cluburl = urldict['ClubView'].path(actobj.club.slug)
		if (not hasActPrivilige(user, actobj, oper,target) ):
			return errorPage ( self.response,  "Can not access",   cluburl,   403)
		if (target):
			targetUser = User(target)
			if(not targetUser):
				return errorPage ( self.response,  "Illegal access",   cluburl,   403)
		else: #if target omitted, use current user as target
			targetUser = user
			
		mem = Membership.between (targetUser, actobj.club)
		if (not mem):
			return errorPage ( self.response,  "Not a member",   cluburl,   403)
		
		acturl = urldict['ActivityView'].path(id)
		if (oper == 'join'):
			actp = ActivityParticipator.between (mem, actobj)
			if (not actp):
				actp = ActivityParticipator(member = mem, activity = actobj)
				actp.put()
			return infoPage (self.response, "Successfully Joined", "%s has join activity %s" % (mem.name, actobj.name), acturl)
		elif (oper == 'quit'):
			actp = ActivityParticipator.between(mem, actobj)
			if (actp):
				if (actp.confirmed):
					return errorPage ( self.response,  "Cannot delete confirmed participator",   acturl,   403)
				else:
					actp.delete()
			return infoPage (self.response, "Successfully Quited", "%s success quit activity %s" % (mem.name, actobj.name), acturl)
		elif (oper == 'confirm'):
			actp = ActivityParticipator.between(mem, actobj)
			if (actp):
				actp.confirmed = not actp.confirmed 
				actp.put()
				return infoPage (self.response, "Successfully Confirmed", "success confirmed %s join activity %s" % (mem.name, actobj.name), acturl)
			else:
				return errorPage ( self.response,  "No Such a Member",   acturl,   404)
		elif (oper == 'bill'):
			return errorPage ( self.response,  "Not Implemented",   acturl,   501)

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
				if (self.request.get ('delete', False)):
					actobj.delete()
					return infoPage (self.response, "Successful deleted", "Deleted Activity %s" % actobj.name, "/")
				self.updateObject(actobj)
				key = actobj.put()
				if (key):
					return errorPage( self.response,  "Successfully storing this Activity",   									urldict['ActivityView'].path(key.id()),   200)
				else:
					return errorPage( self.response,  "Error while storing this Activity",   									urldict['ActivityEdit'].path(actobj.key().id()),   501)
		else:
			return errorPage( self.response,  "No such Activity",   urldict['ClubList'].path(),   404)

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
			errorPage ( self.response,  "Not login",   create_login_url(self.request.url),   403)
			return False
		if (not hasClubPrivilige(user, self.actobj.club, "newact")):
			errorPage ( self.response,  "Not Authorized to edit",   urldict['ClubView'].path(self.actobj.club.slug),   403)
			return False
		return True
