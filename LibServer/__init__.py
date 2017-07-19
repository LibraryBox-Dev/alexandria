"""
The flask application package.
"""

from configparser import ConfigParser
from flask import Flask,render_template,Config,session,request,abort
import base64
from functools import wraps
from flask import g,request,redirect,url_for
import itsdangerous


class LibConfig(Config):
    tainted=False
    def __init__(self, *args, **kwargs):
        """
        LibConfig is essentially just a wrapper around
        a ConfigParser that reads the combined configuration
        files from the command line (typically).
        """
        self.localconf = ""
        self.baseconf = "" 
        self.parser = None
        self.tainted = False
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

    def getBool(self,section,option,default=True):
        if not self.parser.has_section(section):
            return default
        elif not self.parser.has_option(section,option):
            return default
        else:
            return self.parser.getboolean(section,option)

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


def needs_authentication():
    def auth_chk_wrapper(f):
        @wraps(f)
        def deco(*args, **kwargs):
            if "auth" in session:
                print(">> AUTH: {0}".format(session["auth"]))
            if ( not 'authenticated' in session )  or session["authenticated"] == False:
                # calculate next
                # now, we're going to sign it.
                notary = itsdangerous.URLSafeSerializer(app.secret_key)
                signed_next = notary.dumps(request.full_path)
                return redirect(url_for('authenticate',next=signed_next))
            else:
                return f(*args, **kwargs)
        return deco
    return auth_chk_wrapper


@app.route("/auth/",methods=["GET","POST"])
def authenticate():
    next = None
    if 'next' in request.args:
        next = request.args["next"]
    if request.method == "POST":
        # Check if we're correct.
        passphrase = app.config.get("general","admin_key")
        # Check the request
        chkpass = request.form["password"]
        print("Comparing {0} == {1} ? ".format(passphrase,chkpass))
        if(passphrase == chkpass):
            print("Successful login!")
            session["authenticated"]=True
            # redirect off
            if request.form["next"] == "":
                print("No redirect specified. We're going home.")
                return redirect(url_for("home"))
            else:
                # Check to see if it's safe
                notary = itsdangerous.URLSafeSerializer(app.secret_key)
                try:
                    print("We got a next, checking that it's safe")
                    safe_next = notary.loads(request.form["next"])
                    print("Was safe, next={0}".format(safe_next))
                    return redirect(safe_next)
                except itsdangerous.BadSignature as e:
                    print(e)
                    abort(500)
        else:
            session["authenticated"]=False
            return render_template("login.html",fail=True,next=next);
    else:
        # are we already authenticated?
        if "authenticated" in session and session["authenticated"] == True:
            return redirect(url_for("home"))
        else:
            return render_template("login.html",next=next)

@app.route("/auth/logout")
def logout():
    session["authenticated"] = False
    return redirect(url_for('home'))


@app.route('/')
def home():
    # There should be more things here. I'm not sure what to put here, but there needs to be more here.
    # Ideas are in TODO, but include a list of contents and the dixed they take up.
    # Collection lists would be nice too.
    return render_template('index.html',year=2017,title="Hello!")
