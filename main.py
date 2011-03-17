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
from google.appengine.ext.webapp.util import run_wsgi_app
from controlers import *

def str_to_class(str):
	return eval(str)

pathPatList = [(urldict[key].pattern, str_to_class(key)) for key in urldict]

application = webapp.WSGIApplication( pathPatList, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
	main()
