# -*- coding: utf-8 -*-
import os

import xbmc
import xbmcaddon
import xbmcgui

from bottle import template, Bottle, ServerAdapter, auth_basic
from resources.lib.control import setting
from wsgiref.simple_server import WSGIServer

try:
    from typing import Union
except:
    pass

TEMPLATES = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'templates')


class WSGIRefServer(ServerAdapter):
    srv = None  # type: Union[None,WSGIServer]

    def run(self, app):  # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self):  # Prevent reverse DNS lookups please.
                return self.client_address[0]

            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls = self.options.get('server_class', WSGIServer)

        if ':' in self.host:  # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        self.srv = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.srv.serve_forever()


def is_authenticated_user(user, password):
    return user == setting('web_interface_user') and password == setting('web_interface_pwd')


def get_template(name):
    template_file = os.path.join(TEMPLATES, '{}.html'.format(name))
    if not setting('web_interface_debug'):
        return template_file
    with open(template_file, 'r') as f:
        return f.read()


bottle_app = Bottle()


@bottle_app.route('/')
@auth_basic(is_authenticated_user)
def index():
    return template(get_template('index'))


bottle_server = None  # type: Union[None,WSGIRefServer]


def start():
    global bottle_server
    bottle_server = WSGIRefServer(host='0.0.0.0', port=setting('web_interface_port'))
    try:
        bottle_app.run(server=bottle_server)
    except Exception as e:
        xbmcgui.Dialog().notification('Error', str(e))


def stop():
    if bottle_server.srv is None:
        return
    try:
        bottle_server.srv.shutdown()
        bottle_server.srv.server_close()
        bottle_app.close()
    except Exception as e:
        xbmcgui.Dialog().notification('Error', str(e))
