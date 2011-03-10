from google.appengine.ext import db

class Club(db.Model):
	owner = db.UserProperty()
	name = db.StringProperty(multiline=False)
	def __init__(self, keyname, *args, **kw):
		Club.__init__(self, key_name=keyname, *args, **kw)

