"""
The flask application package.
"""

from configparser import ConfigParser
from flask import Flask,render_template,Config
class LibConfig(Config):
    def __init__(self, *args, **kwargs):
        """
        LibConfig is essentially just a wrapper around
        a ConfigParser that reads the combined configuration
        files from the command line (typically).
        """
        self.localconf = ""
        self.baseconf = "" 
        self.parser = None
        Config.__init__(self, *args, **kwargs)
    def get(self, section, option, default=None):
        """
        Get a configuration item from the loaded configuration
        files.

        If the section or configuration is not declared, the
        default value is returned. 
        """
        if self.parser.has_section(section) == False:
            return default
        if not self.parser.has_option(section,option):
            return default
        return self.parser.get(section, option)

    def load(self, baseconfig, localconfig):
        """
        Load a set of configuration files.
        """
        self.parser = ConfigParser()
        self.parser.read(baseconfig)
        self.parser.read(localconfig)

        self.localconf = localconfig
        self.baseconf = baseconfig

class LibFlask(Flask):
    config_class = LibConfig

    def __init__(self,*args, **kwargs):
        Flask.__init__(self, *args, **kwargs)


app = LibFlask(__name__)

@app.route('/')
def home():
    # There should be more things here. I'm not sure what to put here, but there needs to be more here.
    # Ideas are in TODO, but include a list of contents and the dixed they take up.
    # Collection lists would be nice too.
    return render_template('index.html',year=2017,title="Hello!")

