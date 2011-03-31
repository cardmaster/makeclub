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
'''
We use this rule:
/clubs -> 				list clubs, or give more search query
/club/<slug> 			display one club(slug=<slug>), if not exists, return 404
/club/<slug>/edit		edit club with slubg=<slug>, if not exists, create one
/club/<slug>/delete		delete club with slubg=<slug>, if not exists, create one
/member/<slug>[/<user>]	edit membership of club(slug=<slug>), user=<user>(current_user if omitted),
						when post data to a non-exits membership, will cause a create.
/activity/<slug>/<aid>	display activity of a club(slug=<slug>, aid=<aid)
/activity/<slug>/<aid>/edit	edit activity of a club(slug=<slug>, aid=<aid)
/activity/<slug>/<aid>/(join|quit|confirm)	join an activity of a club(slug=<slug>, aid=<aid), if specify an 'targetUser'
							field in request data, will cause this targetUser join this activity
'''

import re
import os.path 
pathjoin = os.path.join

def extPattern(base):
	return base + '($|/.*)'
class ModuleUrlConf(object):
	@staticmethod
	def generatePattern(base):
		return (base % '(\S+)')
	def __init__(self, base, pattern=''):#Base url must have a %s, to specify the variable part
		self.base = base
		if (not pattern):
			self.pattern = ModuleUrlConf.generatePattern(base)
		else:
			self.pattern = pattern
	def path(self, *args):
		strs = tuple ([str(arg) for arg in args])
		return self.base % strs
	def analyze(self, path):
		reg = re.compile(self.pattern)
		mat = reg.match (path)
		if (mat):
			try:
				return mat.groups()
			except:
				return []
		else:
			return []

from helper import splitPath
class MemberUrlConf(ModuleUrlConf):
	def path(self, slug, user=''):
		return ModuleUrlConf.path(self, slug, user)
	def analyze(self, path):
		result = splitPath(path, '/member', 2)
		return result

urldict = dict (
	ClubList = ModuleUrlConf('/clubs', extPattern('(/$|/clubs)') ),
	ClubView = ModuleUrlConf('/club/%s', '/club/(\S+)/?$'),
	ClubEdit = ModuleUrlConf('/club/%s/edit', '/club/(\S+)/edit/?$'),
	Member   = MemberUrlConf('/member/%s/%s', '/member/.*'),
	ActivityView = ModuleUrlConf('/act/id/%s', '/act/id/(\d+)/?$'),
	ActivityEdit = ModuleUrlConf('/act/id/%s/edit', '/act/id/(\d+)/edit/?$'),
	ActivityParticipate = ModuleUrlConf('/act/id/%s/%s', '/act/id/(\d+)/(join|quit|confirm|bill)/?$'),
	ActivityNew  = ModuleUrlConf('/act/new/%s', '/act/new/(\S+)/?$'),
	Test     = ModuleUrlConf('/test/%s', extPattern('/test'))
)
