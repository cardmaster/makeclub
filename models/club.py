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

