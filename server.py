from twisted.web import server, resource, static, twcgi
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.wsgi import WSGIResource
from reel import app
from reel import settings as reel_config
from wsgiref.handlers import format_date_time as format_date
from datetime import date, timedelta
from time import mktime

'''
   Sets the cache headers for a (static resource) request
'''
def cache(request, expires=30, public=True):
    #set expires header
    expiry = (date.today() + timedelta(expires)).timetuple()
    request.setHeader("expires" , format_date(mktime(expiry)))

    cache_control = "max-age=" + str(60*60*24*expires)
    if public:
        cache_control += ", public"
    else:
        cache_control += ", private"
    request.setHeader("cache-control", cache_control)

    return request

class ResponseFile(static.File):
	def render_GET(self, request):
		cache(request)
		return static.File.render_GET(self, request)

class Root( Resource ):
    """Root resource that combines the two sites/entry points"""
    WSGI = WSGIResource(reactor, reactor.getThreadPool(), app)
    def getChild( self, child, request ):
        request.prepath.pop()
        request.postpath.insert(0,child)
        return self.WSGI
    def render( self, request ):
        """Delegate to the WSGI resource"""
        return self.WSGI.render( request )
	

root = Root()
root.putChild("movie-directory", ResponseFile(reel_config('movie_path')))

site = server.Site(root)
reactor.listenTCP(reel_config('port'), site)
reactor.run()
