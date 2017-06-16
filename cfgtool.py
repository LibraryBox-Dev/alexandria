from ConfigEngine.Generators import engine

import sys
import os


engine.setSearchPath([os.path.join(os.getcwd(),"config.ini")])

engine.runGenerator("dnsmasq")