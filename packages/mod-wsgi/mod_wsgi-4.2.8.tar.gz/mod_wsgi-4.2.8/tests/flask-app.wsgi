from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<html><body>Hello World!</body></html>"

from mod_wsgi.toolbar import Middleware
from newrelic.agent import get_browser_timing_header, get_browser_timing_footer

class RumMiddleware(Middleware):
    def insertable(self, environ):
        return get_browser_timing_header() + get_browser_timing_footer()

application = RumMiddleware(app)
