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
from models import Club, conf, Membership, ActivityParticipator, ActivityBill

operations = [
	"listClubs",
	"createClub",
	"deleteClub"
]

clubOperations = [
	"view",
	"edit",
	"delete",
	"join",
	"membership", #For edit memebership or create a membership
	"finance", #Could manage club balance and member's balance
	"arrange",
	"finish",
	"newAct",
	"quit",
	"privGrant"
]

actOperatoins = [
	"view",
	"edit",
	"join",
	"confirm",
	"bill",
	"rebill",
	"quit"
]
class AccessUser(object):
	def __init__(self, user):
		if (not user):
			user = users.get_current_user()
		self.user = user
		self.currentCheck = None
	def can(self, operation, *args):
		self.currentCheck = operation
		methodName = "can_" + operation
		defaultCheckerName = "defaultChecker"
		if ( not hasattr(self, methodName) ) :
			if (hasattr(self, defaultCheckerName)):
				methodName = defaultCheckerName
			else:
				return False
		checker = getattr(self, methodName)
		if (not checker or not callable(checker)):
			return False
		else:
			return checker(*args)
class SystemUser(AccessUser):
	def can_listClubs(self, *args):
		return True
	def can_createClub(self, *args):
		cq = Club.all()
		if (not self.user):
			return False
		cq.filter('owner =', self.user)
		if (cq.count() < conf.MaxClubsPerUser):
			return True
		elif ( users.is_current_user_admin() and self.user == users.get_current_user()):
			return True
		else:
			return False
	
class ClubUser(AccessUser):
	def __init__(self, user, club):
		super(ClubUser, self).__init__(user)
		self.club = club
		if (club.is_saved()):
			self.member = Membership.between(user, club)
		else:
			self.member = None
	def isClubOwner(self):
		return self.user == self.club.owner
	def hasMemberPrivilige(self, *args):
		member = self.member
		if (member):
			return self.currentCheck in member.privilige
		else:
			return False
	def can_view(self, *args):
		if (self.club.isPublic) :
			return True
		elif (self.member):
			return True
		return False
	def can_join(self, *args):
		return (self.club.isPublic) 
	def can_membership(self, *args):
		(target, ) = args
		if (self.user.email() == target): 
			if (self.member): #This is edit own membership
				return True
			else:#This would be consider as a join situation
				return self.can("join")
		else: #Consitor as membership
			return self.defaultChecker()
	def defaultChecker(self, *args):
		return self.isClubOwner() or self.hasMemberPrivilige()

'''
Activity Has 4 operations, every member ship of current club could
view this activity's information, and every member could join this act
but ONLY the organizer could confirm a member's join
And send the bill to everybody, by default, the bill's amout will calculated
by the time duration of a participator
'''
class ActivityUser(AccessUser):
	def __init__(self, user, act):
		super(ActivityUser, self).__init__(user)
		self.act = act
	def isUserOrganizer(self):
		return self.act.organizer == self.user
	def isUserClubMember(self):
		return Membership.between(self.user, self.act.club)
	def can_view(self, *args):
		#Every body can view an activity
		return True
	def can_quit(self, *args):
		parti = ActivityParticipator.between(self.user, self.act)
		if (parti):
			return not parti.confirmed
		return False
	def can_bill(self, *args):
		if (self.act.isBilled):
			return self.can("rebill", *args)
		else:
			return self.defaultChecker(*args)
	def defaultChecker(self, *args):
		organizerOnly = ["edit", "confirm", "bill", "rebill"]
		selfOnly = ["confirm"]
		memberOnly = ["view", "join"]
		target = None
		if (args):
			(target, ) = args
		if ((self.currentCheck in memberOnly) and self.isUserClubMember()):
			return True
		if ((self.currentCheck in selfOnly) and target == self.user):
			return True
		if ( (self.currentCheck in organizerOnly) and self.isUserOrganizer()):
			return True
		return False
	
def isAccessible (user, operation, *args):
	auobj = SystemUser(user)
	return auobj.can(operation, *args)

def hasClubPrivilige (user, club, operation, *args):
	auobj = ClubUser(user, club)
	return auobj.can(operation, *args)

def hasActPrivilige (user, act, operation, *args):
	auobj = ActivityUser(user, act)
	return auobj.can(operation, *args)

