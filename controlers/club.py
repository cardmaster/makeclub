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
from google.appengine.ext import webapp
from template import render
from errors import errorPage
from models import Club
from access import isAccessible
from url import cluburl
from helper import lastWordOfUrl
from access import hasClubPrivilige
from url import urlconf

class ClubList(webapp.RequestHandler):
	def __init__(self,
			template='clublist.html', *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template

	def get(self, *args):
		if (isAccessible('', 'listclubs')):
			clubs = Club.all()
			vars = dict (clubs=Club.all(), cluburl=cluburl)
			self.response.out.write (render(self.template, vars) )
		else:
			errorPage("Not Accessible", users.create_login_url(self.request.uri), self.response)

from google.appengine.api import users
class ClubView(webapp.RequestHandler):
	def __init__(self, 
			template='clubview.html', *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		self.template = template

	def get(self, *args):
		path = self.request.path
		slug = lastWordOfUrl(path)
		if (slug):
			club = Club.getClubBySlug(slug)
		if (club):
			templatevars = dict(club = club )
			user = users.get_current_user()
			if (user and hasClubPrivilige(user, club, 'join')): #Could Join
				templatevars['userName'] = user.nickname()
				templatevars['userEmail'] = user.email()
			else:
				templatevars['loginUrl'] = users.create_login_url(self.request.uri)
			self.response.out.write (render(self.template, templatevars) )
		else:
			self.response.set_status(404)
			errorPage("Club Not Found", urlconf.clubListPath(), self.response)
			

