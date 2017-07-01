"""
The flask application package.
"""

from configparser import ConfigParser
from flask import Flask,render_template,Config
class LibConfig(Config):
    def __init__(self, *args, **kwargs):
        self.localconf = ""
        self.baseconf = "" 
        self.parser = None
        Config.__init__(self, *args, **kwargs)
    def get(self, section, option, default=None):
        if self.parser.has_section(section) == False:
            return default
        if not self.parser.has_option(section,option):
            return default
        return self.parser.get(section, option)

    def load(self, baseconfig, localconfig):
        self.parser = ConfigParser()
        self.parser.read(baseconfig)
        self.parser.read(localconfig)



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

