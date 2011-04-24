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
class AccessUser:
	def __init__(self, user):
		self.user = user
	def can(self, operation, *args):
		checker = getattr(self, "can_" + operation)
		if (not checker or not callable(checker)):
			return False
		else:
			return checker(*args)
class SystemUser(AccessUser):
	def can_listClubs(self, *args):
		return True
	def can_createClub(self, *args):
		return users.is_current_user_admin()
	
class ClubUser(AccessUser):
	def __init__(self, user, club):
		super(ClubUser, self).__init__(user)
		self.club = club
	
def isAccessible (user, operation, *args):
	auobj = SystemUser(user)
	return auobj.can(operation, *args)

def hasClubPrivilige (user, club, operation, *args):
	return True

def hasActPrivilige (user, act, operation, *args):
	return True

