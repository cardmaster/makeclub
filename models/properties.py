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
from decimal import Decimal,getcontext
class MoneyProperty(db.StringProperty):
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

class BillProperty(db.StringListProperty):
	data_type = list
	
	def __init__(self, *args, **kw):
		db.StringListProperty.__init__(self,  *args, **kw)
		self.tuplist = []
	
	def get_value_for_datastore(self, mi):
		#tuplist = self.tuplist
		serl = self.serializeTuplist(self.tuplist)
		return serl
	
	def serializeTuplist(self, tuplist):
		storlist = []
		for tup in tuplist:
			storlist.append(str(tup[0]))
			storlist.append(str(tup[1]))
		return storlist
	
	def toTupleList(self, plainlist):
		i = -1
		key = ''
		output = []
		for str in plainlist:
			i += 1
			if (isinstance(str, tuple)): output.append(str)
			if (i % 2 == 1):
				try:
					output.append( (key, Decimal(str)) )
				except:
					continue
			else: 
				key = str
		return output
		
	#Actually, this validate function will do the conversion work.
	def validate(self, value):
		tupl = self.toTupleList(value)
		self. tuplist = tupl
		return tupl

		
	def default_value(self):
		return []
	
	def make_value_from_datastore(self, value):
		strlist = super(BillProperty, self).make_value_from_datastore(value)
		output = self.toTupleList(strlist)
		self.tuplist = output
		return output
	
	
