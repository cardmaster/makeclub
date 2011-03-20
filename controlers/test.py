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

from google.appengine.ext import webapp
from google.appengine.ext import db
from models import Activity, Membership
class Test(webapp.RequestHandler):
	def __init__(self, *args, **kw):
		webapp.RequestHandler.__init__(self, *args, **kw)
	def dbg(self, lb = True, *args):
		self.response.out.write( (' '.join([str(arg) for arg in args])) )
		if (lb):
			self.response.out.write( "<br />\n" )
	def cleanUp(self):
		allacts = Activity.all(keys_only=True)
		for act in allacts:
			self.dbg ("delete", act)
			db.delete(act)
	def get(self, *args):
		respo = self.response.out.write
		output = self.dbg
		
		respo ("<html><head><title>Test</title></head><body>")
		if (self.request.path.endswith('/clean')):
			output ("Begin Clean Up")
			self.cleanUp()
			output ("Cleaning up done")
			return
		output("Now let's go")
		billList = [('Cort', '75'), ('Balls', '25')]
		output ("BillList: ", billList)
		
		allacts = Activity.all()
		for act in allacts:
			bill = act.bill
			for entry in bill:
				output (False, "Entry:", entry, ",")
			output()
			output ("acts :", act.key(), " Expanse Bill: ", bill)
		
		mem = Membership.all().get()
		act = Activity(organizer = mem.user, club = mem.club, bill = billList, expense = '100' )
		output ("Expense: ", act.expense)
		output ("Now, put")
		key = act.put()
		output ("Act Saved: ", act.is_saved(), "Key is ", key)
		respo("</body></html>")
