import configparser
import sys
import io


def toBool(value):
    truevals = ["1", 'true', 'yes', 'y', 'on']
    falsevals = ['0','false','no','n', 'off']

    if value.lower() in truevals: return True
    elif value.lower() in falsevals: return False
    else: raise ValueError("Invalid value '{0}' - cannot convert to boolean.")

def writeLines(strio, lines):
    for line in lines:
        strio.write(line+'\n')

class ConfigEngine(object):
    """
    The ConfigEngine is responsible for handling the generation of configuration files from a set of INI files. 

    The goal of this is to take a set of layers (like ogres) of INI files, merge them together and turn that into a cohesive set of options.
    
    Each generator passes in either a section (name) or lambda that matches sections (a la filter). There may be multiple generators per section and
    multiple sections per generator. Genrators may be explicitly called as well.

    To use the ConfigEngine, create an instance of it and use the `instance.generator(...)` decorator. 

    Generators should produce a number outputs (streamIO) and consume a dictionary, as well as a string that idenfies the specific section it is being run against.

    Generators that create multiple outputs should have one generator call per output type. Each will get run.
    Generators may be decorated with a @filename decorator that specifies the filename that should be produced, or otherwise it will be the name of the section that
    was presented.
    """
    generators = dict()
    searchpath = dict()
    parser = None

    def __init__(self, searchpath = []):
        self.generators = dict()
        self.searchpath=searchpath
        # load each item in the search path into a config parser.
        self.setSearchPath(searchpath)

    def setSearchPath(self, path):
        self.searchpath = path
        self.parser = configparser.ConfigParser()
        for p in self.searchpath:
            self.parser.read(p)

    def generator(self, description,needs_argument=False):
        def rGenerator(func):
            name = func.__name__
            if name in self.generators:
                raise ValueError("Can't add generator twice!")
            self.generators[name] = {"name":name,"description":description,"func": func, "needs_argument":needs_argument }
            return func
        return rGenerator

    def namespace(self,namespace):
        """
        declares that there is a namespace for this generator for assertions on argument section.
        """
        def rGenerator(func):
            name = func.__name__
            if name not in self.generators:
                raise ValueError("undeclared generator {0}".format(name))
            self.generators[name]["namespace"] = namespace
            return func
        return rGenerator

    def assertConfig(self, section, keys):
        def rDecorator(func):
            name = func.__name__
            if name not in self.generators:
                raise ValueError("Undeclared generator {0}".format(name))
            # We want to make sure that a specific section has keys.
            if section == None:
                # the None section is special: 
                # The None section is used to declare that these are what the *argument* section must
                # contain when called. This makes it possible to require certain things first.
                self.generators[name]["arg_requires"] = keys
            else:
                # In all other cases, we want to make sure that the section contains those specific keys.
                if "requires" not in self.generators[name]:
                    self.generators[name]["requires"] = dict()
                self.generators[name]["requires"][section] = keys
            # return the original function as we're not actually wrapping it in anything. 
            return func
        return rDecorator

    def runGenerator(self,name,argument=None,outfile=sys.stdout):
        """
        Runs a specific generator.

        Arguments:

        name        name of the specific parser
        argument    Argument to be passed to the generator. May not be none for generators which take an argument.


        """

        # First, get the generator out of the generator pool:

        if name not in self.generators:
            raise ValueError("There is no generator by the name {0}".format(name))


        tGenerator = self.generators[name]

        # tGenerator should have the following keys:
        # name (the name of the generator)
        # func (a callable)
        # needs_argument (should we pass an argument?)

        # This is where we do value checking.

        # If the dictionary that contains the required keys for sections exists, we're going to get the options within
        # those sections and make sure that that section has the keys that are marked as being required.
        # If any of those keys are not there, print out a message. If we've encoutered an error, exit with a return of -1
        has_missing = False
        
        if "requires" in tGenerator:
            # we require something. double check. 
            for section in tGenerator["requires"]:
                for option in tGenerator["requires"][section]:
                    if not self.parser.has_option(section,option):
                        print("Error: Required option {0} not found in section {1}".format(option,section),file=sys.stderr)
                        has_missing=True
                    # / if option not in parser
                # / for option in section
            # for section in generator->requires.

        buffer = io.StringIO()

        arguments = [buffer]

        if(tGenerator["needs_argument"]):
            if argument == None:
                raise ValueError("Can't pass an argument that isn't there.")
            else:
                if "arg_requires" in tGenerator:
                    check_section = argument
                    if "namespace" in tGenerator:
                        check_section = tGenerator["namespace"]+"."+argument
                    for option in tGenerator["arg_requires"]:
                        if not self.parser.has_option(check_section, option):
                            print("Error: Required option {0} not found in section {1}".format(option,check_section),file=sys.stderr)
                            has_missing = True
                arguments.append(argument)
        # call the func with our arguments.

        if has_missing:
            print("Missing options in configuration. Please verify that they are indeed set and your search path is correct. Exiting",file=sys.stderr)
            # And bail.
            return

        # Attempt to do the thing. 
        try:
            tGenerator["func"].__call__(*arguments)
            print(buffer.getvalue(),file=outfile)
        except Exception as e:
            print("Failed to call {0}".format(name),file=sys.stderr)
            print(e, file=sys.stderr)
            print("This was bad, and potentially not your fault. Please check your configuration files.",file=sys.stderr)

    def getGenerators(self):
        return self.generators
    def getGenerator(self,name):
        return self.generators[name]

    def getOption(self,section,option,transform=lambda k:k):
        """
        Get a particular option from the configuration.

        Optionally, a transform is placed against it. For example, a transform that uppercases the stored value
        looks like this:

        `.getOption("general","filepath",transform=lambda v:v.upper())`

        This will return an uppercase value.
        """
        return transform(self.parser.get(section,option))
    def getSection(self, section,predicate=lambda k:True,transformKey=lambda k:k, transform=lambda k:k):
        """
        Returns the values within a section, optionally mangling the values on the way.

        This function can take three optional parameters:

        * predicate: Only these keys from the section will be selected.
        * transform: This function will be run over the value of each key.
        * transformKey: this will be run over each of the 

        predicate does not transform the values before comparing the key and the predicate. All
        transformation is after the list of keys within the section have been filtered by predicate.

        This is intentional; should you need to modify keys BEFORE they are compared, you need to do that in your predicate.

        """

        # This is a complex operation done in a few passes.
        # this is list comprehension on crack.
        # filter(predicate, vals.keys()) => return us the keys we care about.
        # k:transform(vals[k]) turns our values into the values we want.
        # this creates a new dictionary by declaring a template for them.
        # The keys are defined by the filter
        # the values are mangled by the transform
        # 

        vals =  dict(self.parser.items(section))
        
        return { transformKey(k): transform(vals[k]) for k in filter(predicate, vals.keys()) }
        
    def hasSection(self,section):
        """
        returns if a specific section is currently in the configuration
        """
        return self.parser.has_section(section)
    def hasOption(self, section, option):
        """
        returns if a specific section's option is set.
        """
        return self.parser.has_option(section,option)
    def getSections(self):
        """
        returns a list of sections.
        """
        return self.parser.sections()
    def searchSections(self, predicate):
        """
        Returns sections that match the predicate.

        The predicate is put into filter() and should take one argument: The name of the section.
        """
        return filter(predicate, self.getSection())
    

