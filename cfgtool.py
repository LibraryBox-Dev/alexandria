from ConfigEngine.Generators import engine

import sys
import os

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("cfgtool",description="Generate configuration for Alexandria",allow_abbrev=False,add_help=True)
    parser.add_argument("-localconfig",metavar="file",required=True, type=str,help="Local (user) configuration")
    parser.add_argument("-baseconfig",metavar="file",required=True,  type=str,help="System (default) configuration")
    parser.add_argument("-list",action='store_true',help="list all generators.")
    # let's make this easy on ourselves. 
    parser.add_argument('-outfile', type=argparse.FileType('w'), default=sys.stdout)
    # And the meat and potatos of the game. 
    parser.add_argument("types",metavar="kind[:arg]",nargs=argparse.REMAINDER, help="Configuration types to generate")
    
    # parse dem arguments
    args = parser.parse_args()

    outfile = args.outfile

    engine.setSearchPath([args.baseconfig,args.localconfig])
    if args.list:
        gens = engine.getGenerators()
        for gen in gens:
            print("{name:18} | {description}".format(**gens[gen]) )
        sys.exit(0)
        # :3

    # At this point we have the required information (the parser has made sure we have baseconfig and localconfig
    # so we don't need to worry about that)
    #
    # we're going to walk through each of the supplied arguments, then pass those into the engine.

    for arg in args.types:
        # we need to make sure that we have all the info we need.
        # We need to know if that particular generator needs an argument.
        # We're going to do this by getting the specific generator we want. 
        
        # Split the argument into its parts.
        argsplit = arg.split(":")
        if len(argsplit) > 2:
            print("Malformed argument '{0}': too many ':'s".format(arg),file=sys.stderr)
            sys.exit(-1)
        
        generator = engine.getGenerator(argsplit[0])

        genkwargs={"outfile":args.outfile, "name":argsplit[0]}

        if generator["needs_argument"] and len(argsplit) < 2:
            print("Generator {0} needs an argument, none supplied.".format(arg[0]),file=sys.stderr)
            sys.exit(-1)

        if generator["needs_argument"]:
            # Run the generator with the second half of the argument passed to us
            genkwargs["argument"] = argsplit[1]

        engine.runGenerator(**genkwargs)

    # At this point, we're done
    sys.exit(0)
