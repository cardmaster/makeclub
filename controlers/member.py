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
from access import hasClubPrivilige
from helper import lastWordOfUrl

class Member(webapp.RequestHandler):
	def __init__(self, 
		template='member.html', *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template
		
	def post(self, *args):
		self.response.write (render(self.template, locals()))
		
	def get(self, *args):
		user = users.get_current_user()
		slug = lastWordOfUrl(self.request.path)
		club = Club.getClubBySlug(slug)
		if (not hasUserPrivilige(user, club, 'membership')):
			return errorPage ("Can not access", '/', self.response, 403)
		if (club):
			member = Membership (name = user.nickname(), email = user.email(), club=club)
			self.response.write (render(selflf.template, locals()))
		else:
			return errorPage ("No such club", '/', 404)
			
