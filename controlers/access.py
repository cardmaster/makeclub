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
from models import Club, conf

operations = [
	"listClubs",
	"createClub"
]

clubOperations = [
	"view",
	"create",
	"edit",
	"delete",
	"arrange",
	"finish",
	"newact"
]

actOperatoins = [
	"view",
	"edit",
	"join"
]
class AccessUser(object):
	def __init__(self, user):
		self.user = user
	def can(self, operation, *args):
		methodName = "can_" + operation
		if ( not hasattr(self, methodName) ) :
			return false						
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
		cq.filter('owner =', self.user)
		return cq.count() < conf.MaxClubsPerUser
	
class ClubUser(AccessUser):
	def __init__(self, user, club):
		super(ClubUser, self).__init__(user)
		self.club = club
	def can_view(self, *args):
		return True
	def can_create(self, *args):
		return True
	def can_edit(self, *args):
		return True
	def can_delete(self, *args):
		return True
	def can_arrange(self, *args):
		return True
	def can_finish(self, *args):
		return True
	def can_newAct(self, *args):
		return True
	
def isAccessible (user, operation, *args):
	auobj = SystemUser(user)
	return auobj.can(operation, *args)

def hasClubPrivilige (user, club, operation, *args):
	auobj = ClubUser(user, club)
	return auobj.can(operation, *args)

def hasActPrivilige (user, act, operation, *args):
	return True

