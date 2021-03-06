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
from google.appengine.ext import db
from properties import MoneyProperty

class Club(db.Model):
	slug = db.StringProperty(multiline=False, required=True, indexed=True, default="new_club_slug")
	owner = db.UserProperty(auto_current_user = True)
	name = db.StringProperty(multiline=False)
	fund = MoneyProperty(default="0.0")
	intro = db.StringProperty(multiline=True)
	isPublic = db.BooleanProperty(required=True, default=True)
	@staticmethod
	def getClubBySlug(slug):
		q = Club.all()
		q.filter("slug =", slug)
		return q.get()

	@staticmethod
	def getClub(slug):
		ret = Club.getClubBySlug(slug)
		if (ret):
			return ret
		else:
			return Club(slug=slug)
		

