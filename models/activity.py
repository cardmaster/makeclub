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
from properties import MoneyProperty, BillProperty
from club import Club

class Activity(db.Model):
	organizer = db.UserProperty()
	club = db.ReferenceProperty(Club)
	expense = MoneyProperty()
	bill = BillProperty()
	
	def calcExpanse(self):
		return self.expanse
	
	def copy(self, oth):
		self.organizer = oth.organizer
		self.club = oth.club
		self.bill = oth.bill
		self.expense = oth.expanse
		
	@staticmethod
	def between(user, club):
		q = Membership.all()
		q.filter('user = ', user).filter('club = ', club)
		return q.get()
	
#	def put(self):
#		return db.Model.put (self)
		
