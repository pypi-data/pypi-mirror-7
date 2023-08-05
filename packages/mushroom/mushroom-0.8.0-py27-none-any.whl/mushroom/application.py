import logging

from gevent.pywsgi import WSGIServer
from mushroom.http import HttpError, HttpMethodNotAllowed, \
        HttpNotFound, HttpUnauthorized, HttpInternalServerError, \
        HttpNotImplemented, HttpRequest, HttpResponse, JsonResponse, \
        WebSocketTransport, PollTransport
from mushroom.rpc import Message, dummy_rpc_handler
from mushroom.session import session_id_generator, Session, SessionList, \
        SessionHandler


logger = logging.getLogger('mushroom.application')


class Application(object):

    def __init__(self, rpc_handler=None, session_handler=None):
        self.sessions = SessionList()
        self.sid_generator = session_id_generator()
        self.rpc_handler = rpc_handler or dummy_rpc_handler
        self.session_handler = session_handler or SessionHandler()

    def __call__(self, environ, start_response):
        try:
            try:
                request = HttpRequest(environ)
                response = self.request(request)
            except Exception as e:
                if isinstance(e, HttpError):
                    raise
                else:
                    logger.exception(e)
                    raise HttpInternalServerError
        except HttpError as e:
            response = HttpResponse(e.code, e.message, extra_headers=e.headers)
        # If the connection has switched to the WebSocket protocol no
        # response is expected. In this case the WSGI application simply
        # needs to returns None.
        if response:
            start_response(response.code, response.headers.items())
            return [response.content]

    def request(self, request):
        # / -> Authentication and connection boostrapping
        if not request.path:
            return self.bootstrap(request)
        # /.*/
        if len(request.path) == 1:
            try:
                sid = request.path[0]
                session = self.sessions[sid]
            except KeyError:
                raise HttpNotFound
            return session.transport.handle_http_request(request, session)
        raise HttpNotFound

    def bootstrap(self, request):
        # Only allow POST requests for bootstrapping
        if request.method != 'POST':
            raise HttpMethodNotAllowed(['POST'])
        for transport in request.data['transports']:
            if transport == 'ws':
                return self.start_session(request, WebSocketTransport())
            if transport == 'poll':
                return self.start_session(request, PollTransport())
        # No suitable transport found
        raise HttpNotImplemented('No suitable transport found')

    def start_session(self, request, transport):
        session = Session(self.sid_generator.next(), transport, self.rpc_handler)
        if not self.session_handler.authenticate(session, request.data.get('auth', None)):
            raise HttpUnauthorized
        self.sessions.add(session)
        self.session_handler.connect(session)
        @transport.state.subscribe
        def state_listener(state):
            if state == 'DISCONNECTED':
                self.sessions.remove(session)
                self.session_handler.disconnect(session)
        return JsonResponse(transport.get_handshake_data(request, session))
