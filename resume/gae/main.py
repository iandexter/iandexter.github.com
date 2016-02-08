import webapp2 as webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class AllHandler(webapp.RequestHandler):
    def get(self):
        self.redirect("http://www.iandexter.net/resume/", True)

app = webapp.WSGIApplication([('/.*', AllHandler)])

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
