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
from google.appengine.ext.webapp import template
class ClubEdit(webapp.RequestHandler):
	def __init__(self, 
		template=os.path.join(os.path.dirname(__file__), '../templates/default/clubedit.html'), *args, **kw ):
		webapp.RequestHandler.__init__(self, *args, **kw)
		
	def post(self, *args):
		pass
	
	def get(self, *args):
		pass
