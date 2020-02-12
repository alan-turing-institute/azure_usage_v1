#!/usr/bin/env python

from bokeh.server.server import Server

from tornado.ioloop import IOLoop

from .bokeh_server import modify_doc

from .constants import (
    URL_PARAM_REPORT, 
    URL_PARAM_SUB_IDS, 
    URL_PARAM_DT_FROM, 
    URL_PARAM_DT_TO)

def bk_worker(origin, bport):
    """ A worker to run Bokeh application

    Args:
        origin - The origin of the websocket connections
        bport - The port of the Bokeh webapp
    """

    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py

    server = Server({'/bokeh_server': modify_doc}, io_loop=IOLoop(), 
        allow_websocket_origin=[
            "localhost", #localhost access
            "turingazureusagetest.azurewebsites.net",
            "turingazureusage.azurewebsites.net",
            "%s:%d" % ('localhost', int(bport)), #localhost access
            "%s:%d" % (origin, int(bport)), #origin access
            ],
        port=int(bport))

    server.start()
    server.io_loop.start()

    return server