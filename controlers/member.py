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
from url import urldict

from template import render
from access import hasClubPrivilige
from helper import lastWordOfUrl
from errors import errorPage
from infopage import infoPage

'''	
Every response method will call visit() first, this will load user(operator),
targetUser(Target), and club(Target Club) from the request path,
if no targetUser specified, we'll assume current user as target user
than create a membership between club and targetUser
'''
urlconf = urldict['Member']
cvurlconf = urldict['ClubView']
class Member(webapp.RequestHandler):
	def __init__(self, 
		template='member.html', *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template
		self.club = None
		self.user = None
		self.member = None
		self.targetUser = None
		self.postStatus = ''

	def post(self, *args):
		if (self.visit()): 
			#If find 'delete' in the request data, we'll delete the member specify by the path
			if (self.judgeDelete()):
				self.doDelete()
				infoPage(self.response, "Delete Succeed", "Deleted", urldict['ClubView'].path(self.club.slug))
				return True
			#Esle we'll construct membership object via postdata
			member = self.getPostData()
			if (member.put()):
				self.postStatus = "Succeed"
			self.member = member
			self.get(*args)
			
	#Delete method not supported yet
	def delete(self, *args):
		if (self.visit()):
			if (self.member):
				member = self.member
				member.delete()
				self.member = None
		self.response.write("Succeed!")
			
	#Get method will display the edit form
	def get(self, *args):
		if (self.visit()): 
			club = self.club
			tempvars = dict (user = self.user,
						action = urlconf.path(self.club.slug, self.user.email()),
						member = self.getMember(),
						club   = self.club,
						cluburl= cvurlconf.path(club.slug),
						postStatus = self.postStatus,
						enableFinace = hasClubPrivilige(users.get_current_user(), club, "finance" )
			)
			self.response.out.write (render(self.template, tempvars, self.request.url))
	
	def judgeDelete(self):
		return (self.request.get('delete', '') == "True")
	
	def doDelete(self):
		if (hasClubPrivilige(self.user, self.club, 'deleteMember', self.targetUser.email() )):
			member = self.member
			if (member):
				return member.delete()
		return False		
	
	def dbg(self, *args):
		self.response.out.write(' '.join([str(arg) for arg in args]))
	
	#Create user, club, and member_namebership information according to request path
	def visit(self):
		if (self.club and self.user):
			return True
		#Analyze req path first
		slug, pathuser = urlconf.analyze(self.request.path)
		#Get club
		club = Club.getClubBySlug(slug)
		if (not club):	
			return errorPage ("No such club " + slug, '/clubs', self.response, 404)
	
		#Check user status
		user = users.get_current_user()
		if (not user):
			return errorPage ("User not login", users.create_login_url(self.request.uri), self.response, self.response, 403)
	
		#That the one we modify is the path user. if omitted, user current user as target
		if (pathuser):
			pathuser = users.User(pathuser)
		else:
			pathuser = user
		#@warning: I don't know is it correct to add access control code here
		if (not hasClubPrivilige(user, club, 'membership', pathuser.email())):
			return errorPage ("Can not access", '/', self.response, 403)
		self.user = user
		self.club = club
		self.member = Membership.between(pathuser, club)
		self.targetUser = pathuser
		return True
	
	#Must call after self.visit
	def getPostData(self):
		member = self.getMember()
		getval = self.request.get
		name = getval('name', '')
		email = getval('email', '')
		balance = getval('balance', '')
		
		member.user = self.targetUser
		if (name):
			member.name = getval('name', '')
		elif (not member.name):
			member.name = self.user.nickname()
		if (email):
			member.email = getval('email', '')
		elif (not member.email):
			member.email = self.user.email()	
		if (balance and hasClubPrivilige(users.get_current_user(), member.club, "finance" )):
			member.balance = balance
		return member
		
	#Could not launch if user is none
	def getMember(self, user=''):
		if (not user):
			user = self.targetUser
		if (self.member):
			member = self.member
		else: 
			member = Membership.between (user, self.club)
			if (not member):
				member = Membership (name = user.nickname(), email = user.email(), club=self.club, user = user)
		return member

