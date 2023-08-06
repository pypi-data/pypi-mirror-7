===================
cherrypy.authorizer
===================

Extensible session based authentication and claims based authorization tool for CherryPy.

Includes authentication controllers for default dispatcher and method dispatcher.

Default authentication controllers are provided in `lribeiro.cherrypy.authorizer.authentication` for default
dispatcher and method dispatcher

cherrypy.authorizer is developed with Python3 and tested against Python2.7 and Python3.4

Example:
--------

.. sourcecode:: python

    import cherrypy

    from lribeiro.cherrypy import authorizer
    from lribeiro.cherrypy.authorizer import authorize
    from lribeiro.cherrypy.authorizer.authentication import Identity, AuthControllerDefaultDispatcher

    # authenticator function signature can be whatever you'd like,
    # as soon as you pass the correct parameters via Http POST
    def _authenticator(username, password):
        if username == 'user' and password == 'pass':
            return Identity('id', 'user')


    def _authorizer(claims):
        if 'read' in claims and claims['read'] == 'page':
            return True
        if 'write' in claims and claims['write'] == 'page':
            return True
        return False

    class Area1:
        @cherrypy.expose
        @authorize({'read': 'page'})
        def index(self):
            return 'authorized'


    @authorize
    class Area2:
        @cherrypy.expose
        def index(self):
            return 'authorized'

        @cherrypy.expose
        @authorize({'write': 'site'})
        def restricted(self):
            return 'restricted'

    class Root:
        @cherrypy.expose
        def index(self):
            pass

    @cherrypy.expose
    def process_login(self, username, password):
        try:
            authenticate(username=username, password=password)
            raise cherrypy.HTTPRedirect('/area1')
        except AuthenticationError:
            raise cherrypy.HTTPError(403)


    if __name__ == '__main__':
        conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.authorizer.on': True,
                'auth.authenticator': _authenticator,
                'auth.authorizer': _authorizer,
                'auth.login_page': '/login',
                'auth.login_redirect': '/logged_in',
                'auth.logout_redirect': '/logged_out',
                'auth.unauthorized_redirect': '/unauthorized'
            }
        }

        root = Root()
        root.area1 = Area1()
        root.area2 = Area2()
        root.auth = AuthControllerDefaultDispatcher()

        cherrypy.quickstart(root, '/', conf)


