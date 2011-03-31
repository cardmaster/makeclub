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
	"listclubs",
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

def isAccessible (user, operation, target = None):
	return True

def hasClubPrivilige (user, club, operation, target = None):
	return True

def hasActPrivilige (user, act, operation, target = None):
	return True

