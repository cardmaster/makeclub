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

#Get the last WORDs after the last slash, if no slash in this string, return empty input arg
def lastWordOfUrl(url):
	slug = url
	try:
		slashIndex = slug.rindex('/')
		return slug[slashIndex + 1:]
	except:
		return ''

from urllib import unquote
def splitPath(url, start='', n=2):
	idx = url.rindex(start)
	st = idx + len(start)
	ary = [''] * n
	i = 0
	for part in url[st:].split('/'):
		if (part):
			ary[i] = unquote(part)
			i += 1
			if (i >= n): return ary
	return ary

def addLogInOutUrl(currentUrl, dict):
	user = users.get_current_user()
	if (user):
		dict['userName'] = user.nickname()
		dict['userEmail'] = user.email()
		dict['logoutUrl'] = users.create_logout_url(currentUrl)
	else :
		dict['loginUrl'] = users.create_login_url(currentUrl)
