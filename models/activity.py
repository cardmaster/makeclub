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
from google.appengine.ext import db
from properties import MoneyProperty, BillProperty
from models import Club, Membership
from decimal import Decimal, getcontext
from datetime import datetime

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
	duration = db.FloatProperty(default = -1.0) #Unit is hours
	#Either Confirmed by Organizer or yourself, after confirmed, you cannot quit.
	confirmed = db.BooleanProperty(default = False)
	def __init__(self, *args, **kw):
		super(ActivityParticipator, self).__init__(*args, **kw)
	def copy(self, oth):
		self.expense = oth.expense
		if (not self.confirmed): #Confirmation can not be canceled
			self.confirmed = oth.confirmed
	@staticmethod
	def between(mem, act):
		if (not isinstance(mem, Membership)): #Will be use as user
			user = mem
			mem = Membership.between(user, act.club)
		if (not mem):
			return None
		q = ActivityParticipator.all()
		q.filter('member = ', mem).filter('activity = ', act)
		return q.get()
	@staticmethod
	def ofAct(act):
		q = ActivityParticipator.all()
		q.filter('activity = ', act)
		return q
	
	def put(self):
		oldms = Membership.between(self.member, self.activity)
		entry = self
		if (oldms):
			oldms.copy(self)
			entry = oldms
		return db.Model.put (entry)
	
class ActivityBill(db.Model):
	activity = db.ReferenceProperty(Activity, required=True)
	expenseBill = BillProperty() #e.g., court fee, 100, balls fee 70
	memberBill = BillProperty() #e.g., leaf, 100, wangyang, 200
	createTime = db.DateTimeProperty(auto_now=True, required=True)
	operator = db.UserProperty(required = True, auto_current_user=True)
	isCancelled = db.BooleanProperty(default=False)
	cancelTime = db.DateTimeProperty()
	def cancel(self):
		if (self.isCancelled):
			return True
		self.cancelTime = datetime.now()
		self.isCancelled = True
		for tup in self.memberBill:
			user = users.User(tup[0])
			money = Decimal(tup[1])
			mem = Membership.between(user, self.activity.club)
			if (mem):
				mem.balance = mem.balance + money
	def put(self):
		super(db.Model, self).put()
	@staticmethod
	def getBill(actobj):
		aq = ActivityBill.all()
		aq.filter("activity =", actobj)
		return aq.get()
	@staticmethod
	def generateBill(actobj, allowRebill = False): #Generate a new bill object by given activity object
		oldBill = ActivityBill.getBill(actobj)
		if (not allowRebill and oldBill):
			return None
		if (oldBill):
			oldBill.cancel()
		cost = actobj.bill
		expense = actobj.expense
		actDur = actobj.duration
		persons = ActivityParticipator.ofAct(actobj)
		sumdur = 0.0
		tuplist = list()
		for person in persons:
			duration = person.duration
			if (duration < 0 or duration > actDur):
				duration = actDur
			person.duration = duration
			tup = (person.member.user.email(), duration)
			tuplist.append(tup)
			sumdur += duration
		mb = list()
		for tup in tuplist:
			email = tup[0]
			dur = tup[1]
			rate = duration / sumdur
			mExp = rate * float(expense)
			mDecExp = Decimal(mExp)
			tup = (email, mDecExp)
			mb.append(tup)
		bill = ActivityBill(activity = actobj, expenseBill = actobj.bill, memberBill = mb)
		return bill
