"""
Alexandria development server
"""

from os import environ
import LibServer
from LibServer import app

from LibServer.admin import admin
from LibServer.browser import browser

from argparse import ArgumentParser

if __name__ == '__main__':

    print("LibServer lives in {0}".format(LibServer.__file__))

    parser = ArgumentParser("libserv",description="The Alexandria library service",add_help=True)
    parser.add_argument("-localconfig",metavar="file",required=True, type=str,help="Local (user) configuration")
    parser.add_argument("-baseconfig",metavar="file",required=True,  type=str,help="System (default) configuration")
    parser.add_argument("-debug",action='store_true',help="run the server in debug mode")
    parser.add_argument("-host",type=str,default='localhost',help="Bind to this specific host")
    parser.add_argument("-port",type=int,default=5555)
    parser.add_argument("-no-admin",action='store_true',help="Disable administration panel")
    
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

    app.debug = args.debug

    app.register_blueprint(browser)
    app.register_blueprint(admin,url_prefix='/admin')

    app.run(HOST, PORT)
