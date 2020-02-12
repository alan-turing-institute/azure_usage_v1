#!/usr/bin/env python
import argparse

from threading import Thread

from bokeh.server.server import Server
from bokeh.embed import server_document
from tornado.ioloop import IOLoop

from src_webapp.bokeh_server import modify_doc

from src_webapp.constants import (
    URL_PARAM_REPORT, 
    URL_PARAM_SUB_IDS, 
    URL_PARAM_DT_FROM, 
    URL_PARAM_DT_TO)

from src_webapp.server import bk_worker


def setup():
    """
    Prepared arguments for the command line
    
    """

    parser = argparse.ArgumentParser(description='Flask webframework with embedded Bokeh app.')

    parser.add_argument("-b", "--bport", help="The port of the Bokeh webapp", default=5001)
    parser.add_argument("-o", "--origin", help="The origin of the websocket connections", default="127.0.0.1")

    args = parser.parse_args()
    
    return args

if __name__ == "__main__":

    # Reading in the command line arguments
    args = setup()

    # Running Bokeh server
    bk_worker(args.origin, args.bport)