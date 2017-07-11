#!/usr/bin/env python

"""
Alexandria development server
"""

from os import environ
import LibServer
from LibServer import app
import random, string
from LibServer.admin import admin
from LibServer.browser import browser
from pidfile import PIDFile
from argparse import ArgumentParser

if __name__ == '__main__':

    parser = ArgumentParser("libserv",description="The Alexandria library service",add_help=True)
    parser.add_argument("-localconfig",metavar="file",required=True, type=str,help="Local (user) configuration")
    parser.add_argument("-baseconfig",metavar="file",required=True,  type=str,help="System (default) configuration")
    parser.add_argument("-debug",action='store_true',help="run the server in debug mode")
    parser.add_argument("-host",type=str,default='localhost',help="Bind to this specific host")
    parser.add_argument("-port",type=int,default=5555)
    parser.add_argument("-no-admin",dest="noadmin",action='store_true',help="Disable administration panel")
    parser.add_argument("-pidfile",help="PIDFile to lock against", default="libsrv.pid")

    parser.add_argument("-fcgisocket",type=str,default=None,help="FastCGI socket path.")

    parser.allow_abbrev=False
    args = parser.parse_args()


    app.config["product"] = "PriateBox"
    app.config["version"] = "3.0-NG"
    


    HOST = environ.get('SERVER_HOST', args.host)
    try:
        PORT = int(environ.get('SERVER_PORT', args.port))
    except ValueError:
        PORT = args.port


    # We're going to get our default and overlay configurations.
    # This is being supplied by the command line

    app.config["configfiles"] = [args.baseconfig, args.localconfig]
    app.config["localConfigPath"] = args.localconfig
    app.config["baseConfigPath"] = args.baseconfig

    app.config.load(args.baseconfig, args.localconfig)

    app.config["product"] = app.config.get("alexandria","product", "Alexandria")
    app.config["version"] = app.config.get("alexandria", "version", "(HEAD?)")

    app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


    app.debug = args.debug

    app.register_blueprint(browser)
    if(not args.noadmin):
       app.register_blueprint(admin,url_prefix='/admin')

    
    if( app.debug):
        print("Can't run with PIDfile and debug; ignoring pidfile")
        app.run(HOST, PORT)
    else:
        with PIDFile(args.pidfile):
            app.run(HOST, PORT)
