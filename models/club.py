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
from google.appengine.ext import db
from decimal import Decimal
class FundProperty(db.StringProperty):
	data_type = Decimal
	def __init__(self, *args, **kw):
		db.StringProperty.__init__(self, multiline=False, *args, **kw)
	def get_value_for_datastore(self, mi):
		strv = db.StringProperty.get_value_for_datastore(self, mi)
		return str(Decimal(strv))
	def validate(self, value):
		vv = Decimal(value)
		return vv
	def default_value(self):
		return Decimal('0')
	def make_value_from_datastore(self, value):
		strv = db.StringProperty.make_value_from_datastore(self, value)
		return Decimal(strv)

class Club(db.Model):
	slug = db.StringProperty(multiline=False, required=True, indexed=True, default="new_club_slug")
	owner = db.UserProperty()
	name = db.StringProperty(multiline=False)
	fund = FundProperty()
	intro = db.StringProperty(multiline=True)
	@staticmethod
	def getClub(slug):
		q = Club.all()
		q.filter("slug =", slug)
		res = q.fetch(1)
		for clb in res:
			return clb
		return Club(slug=slug)

