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
from models import Club, Membership
from decimal import Decimal

"""
The reason we seperate date&time is mainly for index the data, so we could use more =
filters in the contoler
"""
class Activity(db.Model):
	name = db.StringProperty(multiline=False, required=True)
	intro = db.StringProperty(multiline=True)
	organizer = db.UserProperty(required = True)
	club = db.ReferenceProperty(Club, required = True)
	startTime = db.DateTimeProperty(indexed=True, auto_now=True, required=True)
	duration = db.FloatProperty(required = True) #Unit is hours
	expense = MoneyProperty()
	bill = BillProperty()
	def __init__(self, *args, **kw):
		super(Activity, self).__init__(*args, **kw)
		self.expense = self.calcExpense()
	
	def calcExpense(self):
		bill = self.bill
		expense = Decimal('0')
		for entry in bill:
			name, exp = entry
			expense += Decimal(exp)
		return expense
		
	def put(self):
		self.expense = self.calcExpense()
		return db.Model.put (self)
	@staticmethod
	def createDefault(user, club):
		if (user and club):
			name = 'New Activity'
			bill = []
			return Activity(organizer = user, club = club, name = name, bill = bill, duration = 2.2)
		else:
			return None

class ActivityParticipator(db.Model):
	activity = db.ReferenceProperty(Activity, required=True)
	member = db.ReferenceProperty(Membership, required=True)
	expense = MoneyProperty(default = '0')
	#Either Confirmed by Organizer or yourself, after confirmed, you cannot quit.
	confirmed = db.BooleanProperty(default = False)
	