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
from url import memberurl, urlconf

from template import render
from access import hasClubPrivilige
from helper import lastWordOfUrl
from errors import errorPage

def analyzePath(url, n=2):
	idx = url.rindex(memberurl)
	st = idx + len(memberurl)
	tuple = [''] * n
	i = 0
	for part in url[st:].split('/'):
		if (part):
			tuple[i] = part
			i += 1
			if (i >= n): return tuple
	return tuple
	
class Member(webapp.RequestHandler):
	def __init__(self, 
		template='member.html', *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template
		self.club = None
		self.user = None
		self.member = None
		self.postStatus = ''
		
	def post(self, *args):
		if (self.visit()): 
			member = self.getPostData()
			if (member.put()):
				self.postStatus = "Succeed"
			self.member = member
			self.get(*args)
	
	def get(self, *args):
		if (self.visit()): 
			club = self.club
			tempvars = dict (user = self.user,
						action = urlconf.memberPath(self.club.slug, self.user.email()),
						member = self.getMember(),
						club   = self.club,
						cluburl= urlconf.clubViewPath(club.slug),
						postStatus = self.postStatus
			)
		self.response.out.write (render(self.template, tempvars))
	
	#Create user, club, and member_namebership information according to request path
	def visit(self):
		if (self.club and self.user):
			return True
		slug, pathuser = analyzePath(self.request.path)
		user = users.get_current_user()
		if (not user):
			return errorPage ("User not login", users.create_login_url(self.request.uri), self.response, self.response, 403)
		club = Club.getClubBySlug(slug)
		#That the one we modify is the path user. if omitted, user current user as target
		if (pathuser):
			pathuser = users.User(pathuser)
		else:
			pathuser = user
		if (not hasClubPrivilige(user, club, 'membership:' + pathuser.email())):
			return errorPage ("Can not access", '/', self.response, 403)
		if (not club):	
			return errorPage ("No such club " + slug, '/', self.response, 404)
		self.user = user
		self.club = club
		self.member = Membership.between(user, club)
		return True
	
	def getPostData(self):
		member = self.getMember()
		getval = self.request.get
		if (getval('name', '')):
			member.name = getval('name', '')
		else:
			if (not member.name):
				member.name = self.user.nickname()
		if (getval('name', '')):
			member.email = getval('email', '')
		else:
			if (not member.email):
				member.email = self.user.email()	
		return member
		
	#Could not launch if user is none
	def getMember(self, user=''):
		if (not user):
			user = self.user
		if (self.member):
			member = self.member
		else: 
			member = Membership (name = user.nickname(), email = user.email(), club=self.club)
		return member
