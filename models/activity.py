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
	expense = MoneyProperty(default=Decimal(0))
	bill = BillProperty()
	isBilled = db.BooleanProperty(default=False)
	def __init__(self, *args, **kw):
		super(Activity, self).__init__(*args, **kw)
		self.expenseBackup = self.expense
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
		moneychg = self.expense - self.expenseBackup
		self.club.fund -= moneychg #When create an activity, will use the club fund, 
		self.club.put()            #And after send bill, those money will be pay by confiredm participators
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
	expense = MoneyProperty(default=Decimal(0))
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
	
'''
The 'oldfund' property here is a quickfix
Cause the GAE will not update the club value when you call bill.cancel()
then newbill.put()
during the put, is you call the 'execute()', in this time,
you can not get the newest value of club.fund, so we use this 'oldfund' to walk-around this problem.
'''
class ActivityBill(db.Model):
	activity = db.ReferenceProperty(Activity, required=True)
	expenseBill = BillProperty(required = True) #e.g., court fee, 100, balls fee 70
	memberBill = BillProperty(required = True) #e.g., leaf, 100, wangyang, 200
	sum = MoneyProperty(default=Decimal(0))
	isExecuted = db.BooleanProperty(default=False)
	createTime = db.DateTimeProperty(auto_now=True, required=True)
	operator = db.UserProperty(required = True, auto_current_user=True)
	isCancelled = db.BooleanProperty(default=False)
	cancelTime = db.DateTimeProperty()
	def __init__(self, oldfund = None, *args, **kw):
		self.oldfund = oldfund
		super(ActivityBill, self).__init__(*args, **kw)
	def cancel(self):
		print "enter cancel method", " isCancelled=", self.isCancelled
		if (self.isCancelled):
			return True
		self.activity.isBilled=False
		self.activity.put()
		self.cancelTime = datetime.now()
		self.isCancelled = True
		for tup in self.memberBill:
			user = users.User(tup[0])
			money = Decimal(tup[1])
			mem = Membership.between(user, self.activity.club)
			if (mem):
				mem.balance = mem.balance + money
				mem.put()
				actp = ActivityParticipator.between(mem, self.activity)
				actp.expense = 0
				actp.put()
		club = self.activity.club
		print "club fund=", club.fund, "-", self.sum
		club.fund -= self.sum #When cancel, not effect
		club.put()	
		print "club fund=", club.fund
		self.put()
	def put(self):
		if (not (self.isExecuted or self.isCancelled)):
			self.execute()
		return super(ActivityBill, self).put()
	#will casue member money decrease
	def execute(self):
		if (self.isExecuted):
			return
		self.isExecuted = True
		self.activity.isBilled=True
		self.activity.put()
		for tup in self.memberBill:
			email = tup[0]
			cost = tup[1]
			user = users.User(email)
			mem = Membership.between(user, self.activity.club)
			bal = mem.balance
			mem.balance = bal - cost
			mem.put()
			actp = ActivityParticipator.between(mem, self.activity)
			actp.expense = cost
			actp.put()
		club = self.activity.club
		if (self.oldfund):
			oldfund = self.oldfund
		else:
			oldfund = club.fund
		print "club fund=", oldfund, "+", self.sum
		club.fund = oldfund + self.sum #When do bill, member's money will go to club's fund
		club.put()			
		print "club fund=", club.fund
	@staticmethod
	def getBill(actobj):
		aq = ActivityBill.all()
		aq.filter("activity =", actobj).filter("isCancelled =", False)
		return aq.get()
	@staticmethod
	def generateBill(actobj, allowRebill = False): #Generate a new bill object by given activity object
		oldBill = ActivityBill.getBill(actobj)
		if (not allowRebill and oldBill):
			return None
		fund = False
		if (oldBill):
			oldBill.cancel()
			fund = oldBill.activity.club.fund
			print "old club fund=", fund
		cost = actobj.bill
		expense = actobj.expense
		actDur = actobj.duration
		persons = ActivityParticipator.ofAct(actobj)
		persons.filter("confirmed =", True)
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
		summoney = Decimal(0)
		mb = list()
		for tup in tuplist:
			email = tup[0]
			dur = tup[1]
			rate = duration / sumdur
			mExp = rate * float(expense)
			mDecExp = Decimal(mExp)
			summoney += mDecExp
			tup = (email, mDecExp)
			mb.append(tup)
		bill = ActivityBill(fund, activity = actobj, expenseBill = actobj.bill, memberBill = mb, sum=summoney)
		return bill
