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

from template import render
from url import urldict
from models import Club, Membership
from errors import errorPage
from infopage import infoPage
from access import hasClubPrivilige, clubOperations 

class ClubPrivilige(webapp.RequestHandler):
	def __init__(self, 
		template='clubpriv.html', *args, **kw ):
		self.template = template
	def get(self, *args):
		if (self.initRequest()):
			currentPriv = self.target.privilige
			tempvars = dict (membership = self.target, 
							operator = self.user, 
							operations = clubOperations,
							currentPriv = currentPriv)
			self.response.out.write (render (self.template, tempvars))
		
	def post(self, *args):
		if (self.initRequest()):
			getval = self.request.get
			getlist = self.request.get_all
			privs = getlist('priv')
			member = self.target
			member.privilige = privs
			member.put()
			infoPage(self.response, "Success", "Success fully enable grant user %s in club %s those privilige: \n (%s)"
					% (self.target.name, self.target.club.name, ', '.join(privs)), self.request.path )
			
	def initRequest(self):
		urlconf = urldict[type(self).__name__]
		slug, useremail = urlconf.analyze(self.request.path)
		club = Club.getClubBySlug(slug)
		if (not club):
			return errorPage(self.response, "No Such Club: '%s'" % slug, urldict['ClubList'].path(), 404)
		user = users.get_current_user()
		pathuser = user
		if (useremail):
			getuser = users.User(useremail)
			if (getuser):
				pathuser = getuser
		if (hasClubPrivilige(user, club, "privGrant", pathuser)):
			self.user = user
			self.target = Membership.between(pathuser, club)
			if (self.target):
				return True
			else:
				return errorPage(self.response, "User %s is not a member of club %s" % (pathuser, slug), urldict['ClubView'].path(slug), 403 )
		else:
			return errorPage(self.response, "Access Deny For Privilige Grant Operation on Club %s, to user %s" % (slug, pathuser), urldict['ClubView'].path(slug), 403 )
