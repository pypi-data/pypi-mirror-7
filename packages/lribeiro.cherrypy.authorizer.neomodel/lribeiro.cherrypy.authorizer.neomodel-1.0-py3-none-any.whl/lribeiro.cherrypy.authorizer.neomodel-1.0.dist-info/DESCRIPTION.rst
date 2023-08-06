===============================
cherrypy-authorizer-mongoengine
===============================

Basic user model, authenticator and authorizer for cherrypy-authorizer and neomodel

Usage:
------

.. sourcecode:: python

    import cherrypy

    from lribeiro.cherrypy.authorizer import authorize
    from lribeiro.cherrypy.authorizer.authentication import AuthControllerDefaultDispatcher

    from lribeiro.cherrypy.authorizer.neomodel.auth import authenticator, authorizer


    class Root:
        @cherrypy.expose
        def index(self):
            return 'index'

        @cherrypy.expose
        @authorize
        def auth_required(self):
            return 'auth required'

        @cherrypy.expose
        @authorize({'read': 'page'})
        def authorized(self):
            return 'authorized'

        @cherrypy.expose
        @authorize({'edit': 'page'})
        def unauthorized(self):
            return 'unauthorized'

    config = {
        '/': {
            'tools.sessions.on': True,
            'tools.authorizer.on': True,
            'auth.authenticator': authenticator,
            'auth.authorizer': authorizer,
            'auth.login_page': '/login'
        }
    }

    if __name__ == '__main__':
        root = Root()
        root.auth = AuthControllerDefaultDispatcher()

        cherrypy.quickstart(root, '/', config)

