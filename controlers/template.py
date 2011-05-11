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
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template
import os
from url import urldict
from helper import addLogInOutUrl

register = template.create_template_register()
	
def templateFolder():
	return (os.path.join(os.path.dirname(__file__), '../templates'))
def templateSet():
	return 'default'

def render(tempname, dict, currentUrl = '/', createLogInOutUrl = True, dbgTemp = False):
	pageFrame = os.path.join(templateFolder(), templateSet(), "pageframe.html")
	dict['bodyTemplate'] = tempname
	if ('pageTitle' not in dict):
		dict['pageTitle'] = tempname[:tempname.rindex('.')]
	if (createLogInOutUrl):
		addLogInOutUrl(currentUrl, dict)
	if (dbgTemp):	
		templateFile = os.path.join (templateFolder(), templateSet(), tempname)
		return template.render(templateFile, dict)
	else:
		return template.render(pageFrame, dict)
	
