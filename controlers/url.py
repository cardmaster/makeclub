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
/activity/<slug>/<aid>/join	join an activity of a club(slug=<slug>, aid=<aid), if specify an 'targetUser'
							field in request data, will cause this targetUser join this activity
'''
import re
import os.path 
pathjoin = os.path.join


cluburl = "/club"
clubjoin = "/club/member"
clubedit = "/club/%s/edit"
clublist = "/clubs"
memberurl = "/member"


def extPattern(base):
	return base + '($|/.*)'
class ModuleUrlConf:
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
		return base % args
	def analyze(self, path):
		reg = re.compile(self.pattern)
		mat = reg.match (path)
		if (mat):
			try:
				return mat.groups()[1:]
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
	clublist = ModuleUrlConf('/clubs', extPattern('/clubs') ),
	clubview = ModuleUrlConf('/club/%s', '/club/(\S+)/?$'),
	clubedit = ModuleUrlConf('/club/%s/edit', '/club/(\S+)/edit/?$'),
	member   = MemberUrlConf('/member/%s/%s', '/member/(\S+)/(\S+)')
)

class UrlConf:
	def memberPath(self, slug='', user=''):
		return (memberurl + '/' + slug + '/' + user)
	
	def memberPattern(self):
		return extPattern(memberurl)
	
	def clubViewPath(self, slug):
		return cluburl + '/' + slug
	
	def clubListPath(self, cond=''):
		return clublist + '/' + cond
	
	def clubEditPath(self, slug):
		return clubedit % slug
	
	def clubListPattern(self):
		return extPattern(clublist)
	
	def clubViewPattern(self):
		return cluburl + '/.*'
	
	def clubEditPattern(self):
		return clubedit % '\S+' + '/?$' 
	  
	def getClubEditSlug(self, path):
		reg = re.compile(clubedit % '(\S+)')
		mat = reg.match (path)
		if (mat):
			try:
				return mat.group(1)
			except:
				return ''
		return ''
		
urlconf = UrlConf()
