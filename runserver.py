"""
Alexandria development server
"""

from os import environ
from LibServer import app

from argparse import ArgumentParser

if __name__ == '__main__':

    parser = ArgumentParser("libserv",description="The Alexandria library service",add_help=True)
    parser.add_argument("-localconfig",metavar="file",required=True, type=str,help="Local (user) configuration")
    parser.add_argument("-baseconfig",metavar="file",required=True,  type=str,help="System (default) configuration")
    parser.add_argument("-debug",default=False,type=bool,help="run the server in debug mode")
    parser.add_argument("-host",type=str,default='localhost',help="Bind to this specific host")
    parser.add_argument("-port",type=int,default=5555)
    parser.allow_abbrev=False
    
    
    args = parser.parse_args()

    HOST = environ.get('SERVER_HOST', args.host)
    try:
        PORT = int(environ.get('SERVER_PORT', args.port))
    except ValueError:
        PORT = 5555


    # We're going to get our default and overlay configurations.
    # This is being supplied by the command line

    app.config["configfiles"] = [args.baseconfig, args.localconfig]

    app.debug = args.debug
    app.run(HOST, PORT)
